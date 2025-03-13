import os
import json
from importlib import import_module
from typing import Dict, Any, List
from contextlib import nullcontext
from langchain_google_genai import GoogleGenerativeAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from langchain.callbacks.tracers import LangChainTracer
from langchain.callbacks.manager import CallbackManager
from langsmith import Client
from prompts import overview_prompt, component_prompt, integration_prompt
from config import MODEL_NAME, TEMPERATURE, MAX_OUTPUT_TOKENS, GOOGLE_API_KEY, ANALYSIS_CHUNK_SIZE, ANALYSIS_CHUNK_OVERLAP
from config import LANGSMITH_API_KEY, LANGSMITH_PROJECT, LANGSMITH_TRACING

class DocumentGenerator:
    def __init__(self, code_analysis: Dict[str, Any]):
        self.code_analysis = code_analysis
        
        # Set up LangSmith tracing
        self.callback_manager = None
        if LANGSMITH_API_KEY:
            tracer = LangChainTracer(project_name=LANGSMITH_PROJECT)
            self.callback_manager = CallbackManager([tracer])
            self.langsmith_client = Client(api_key=LANGSMITH_API_KEY)
            print(f"LangSmith tracing enabled for project: {LANGSMITH_PROJECT}")
        else:
            print("LangSmith API key not found. Tracing disabled.")
        
        # Initialize LLM
        self.llm = GoogleGenerativeAI(
            model=MODEL_NAME,
            google_api_key=GOOGLE_API_KEY,
            temperature=TEMPERATURE,
            max_output_tokens=MAX_OUTPUT_TOKENS,
            callbacks=self.callback_manager
        )
        
        # Initialize text splitter for handling large code bases
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=ANALYSIS_CHUNK_SIZE,
            chunk_overlap=ANALYSIS_CHUNK_OVERLAP
        )
    
    def generate_overview_document(self, output_dir: str) -> str:
        """Generate a high-level software overview document in JSON format."""
        # Prepare data for the overview
        languages = self.code_analysis.get("languages", {})
        key_components = self.code_analysis.get("key_components", [])
        
        # Create code samples from key components (limited to keep prompt size reasonable)
        code_samples = []
        for component in key_components[:3]:  # Limit to top 3 components
            for file in self.code_analysis["files"]:
                if file["path"] == component["path"]:
                    # Truncate content if too large
                    content = file["content"][:2000] + "..." if len(file["content"]) > 2000 else file["content"]
                    code_samples.append(f"File: {file['path']}\n```{file['language'].lower()}\n{content}\n```")
        
        code_samples_text = "\n\n".join(code_samples)
        
        # Run the chain with LangSmith tracing
        with self._get_trace_context("overview_document_generation"):
            chain = overview_prompt | self.llm
            result = chain.invoke({
                "languages": json.dumps(languages, indent=2),
                "components": json.dumps(key_components, indent=2),
                "code_samples": code_samples_text
            })
        
        try:
            # Parse the result to ensure it's valid JSON
            overview_json = json.loads(result)
            
            # Save result to file
            output_file = os.path.join(output_dir, "overview_doc.json")
            with open(output_file, 'w') as f:
                json.dump(overview_json, f, indent=2)
            
            return output_file
        except json.JSONDecodeError:
            # If parsing fails, extract JSON from the response
            print("Warning: LLM response was not valid JSON. Attempting to extract JSON content...")
            json_content = self._extract_json_from_text(result)
            output_file = os.path.join(output_dir, "overview_doc.json")
            with open(output_file, 'w') as f:
                f.write(json_content)
            
            return output_file
    
    def generate_specification_document(self, output_dir: str) -> str:
        """Generate a detailed software specification document in JSON format."""
        # Process code files in chunks to handle large codebases
        all_files = self.code_analysis["files"]
        
        # Sort files by likely importance
        all_files.sort(key=lambda x: self._calculate_file_importance(x))
        
        # Prepare documents for sequential processing
        documents = []
        for file_info in all_files:
            if file_info["content"]:
                doc = Document(
                    page_content=file_info["content"],
                    metadata={"path": file_info["path"], "language": file_info["language"]}
                )
                documents.append(doc)
        
        # Split into manageable chunks if needed
        if sum(len(doc.page_content) for doc in documents) > ANALYSIS_CHUNK_SIZE:
            chunked_documents = self.text_splitter.split_documents(documents)
        else:
            chunked_documents = documents
        
        # Process each chunk and collect information
        component_analyses = []
        component_analyses_json = []
        
        for i, doc in enumerate(chunked_documents[:10]):  # Limit to first 10 chunks for reasonable processing
            with self._get_trace_context(f"component_analysis_{doc.metadata['path']}"):
                chain = component_prompt | self.llm
                result = chain.invoke({
                    "file_path": doc.metadata["path"],
                    "language": doc.metadata["language"],
                    "code": doc.page_content
                })
            
            try:
                # Parse the result to ensure it's valid JSON
                component_json = json.loads(result)
                component_analyses_json.append(component_json)
                component_analyses.append(result)
            except json.JSONDecodeError:
                # If parsing fails, extract JSON from the response
                json_content = self._extract_json_from_text(result)
                if json_content:
                    component_analyses.append(json_content)
                    try:
                        component_analyses_json.append(json.loads(json_content))
                    except:
                        print(f"Warning: Could not parse JSON for component {doc.metadata['path']}")
        
        # Generate integration analysis
        with self._get_trace_context("integration_analysis"):
            chain = integration_prompt | self.llm
            integration_result = chain.invoke({
                "components": "\n\n".join(component_analyses),
                "project_structure": json.dumps(self.code_analysis["project_structure"], indent=2)
            })
        
        try:
            integration_json = json.loads(integration_result)
        except json.JSONDecodeError:
            integration_content = self._extract_json_from_text(integration_result)
            try:
                integration_json = json.loads(integration_content)
            except:
                print("Warning: Could not parse JSON for integration analysis")
                integration_json = {"systemArchitecture": "Error parsing integration analysis"}
        
        # Build final specification document as JSON
        specification_json = {
            "components": component_analyses_json,
            "integration": integration_json,
            "projectStructure": self.code_analysis["project_structure"],
            "technologies": self.code_analysis["languages"],
            "metadata": {
                "generatedAt": str(import_module('datetime').datetime.now()),
                "sourceCodeAnalysisVersion": "1.0"
            }
        }
        
        # Save result to file
        output_file = os.path.join(output_dir, "spec_doc.json")
        with open(output_file, 'w') as f:
            json.dump(specification_json, f, indent=2)
        
        return output_file
    
    def _get_trace_context(self, run_name):
        """Get a context manager for tracing with LangSmith or a no-op context manager if disabled."""
        if LANGSMITH_API_KEY and LANGSMITH_TRACING:
            try:
                # For LangChain 0.1.0+ we use a different approach
                from contextlib import contextmanager
                
                @contextmanager
                def langsmith_context(name):
                    # Set run name via environment variable instead
                    old_run_name = os.environ.get("LANGCHAIN_RUN_NAME")
                    os.environ["LANGCHAIN_RUN_NAME"] = name
                    try:
                        yield
                    finally:
                        if old_run_name:
                            os.environ["LANGCHAIN_RUN_NAME"] = old_run_name
                        else:
                            os.environ.pop("LANGCHAIN_RUN_NAME", None)
                
                return langsmith_context(run_name)
                
            except Exception as e:
                print(f"Warning: Error setting up tracing: {e}. Using null context.")
                return nullcontext()
        else:
            return nullcontext()
    
    def _calculate_file_importance(self, file_info: Dict[str, Any]) -> float:
        """Calculate a heuristic importance score for a file."""
        importance = 0.0
        path = file_info["path"].lower()
        
        # Files that are likely more important
        if any(keyword in path for keyword in ['main', 'app', 'index', 'core']):
            importance += 10.0
            
        if 'test' in path:
            importance -= 5.0  # Tests are less important for specifications
            
        # Consider file size (larger files might contain more logic)
        # But not too large as they might be data files
        size = file_info["size"]
        if 100 <= size <= 10000:
            importance += min(size / 1000, 5.0)
            
        return importance
    
    def _extract_json_from_text(self, text: str) -> str:
        """Extract JSON from text that may contain additional content."""
        import re
        json_pattern = r'```json\s*([\s\S]*?)\s*```|```\s*([\s\S]*?)\s*```|\{\s*"[^"]+"\s*:[\s\S]*\}'
        match = re.search(json_pattern, text)
        
        if match:
            # Get the match from either the first or second group
            json_str = match.group(1) or match.group(2)
            if not json_str:
                # If no match in the code blocks, try to find a JSON object
                match = re.search(r'\{[\s\S]*\}', text)
                if match:
                    json_str = match.group(0)
                else:
                    return "{}"
            return json_str.strip()
        else:
            # If no JSON pattern found, return empty object
            return "{}"


