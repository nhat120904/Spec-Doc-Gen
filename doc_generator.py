import os
import json
from typing import Dict, Any, List
from langchain_google_genai import GoogleGenerativeAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.schema.document import Document
from prompts import overview_prompt, component_prompt, integration_prompt
from config import MODEL_NAME, TEMPERATURE, MAX_OUTPUT_TOKENS, GOOGLE_API_KEY, ANALYSIS_CHUNK_SIZE, ANALYSIS_CHUNK_OVERLAP

class DocumentGenerator:
    def __init__(self, code_analysis: Dict[str, Any]):
        self.code_analysis = code_analysis
        
        # Initialize LLM
        self.llm = GoogleGenerativeAI(
            model=MODEL_NAME,
            google_api_key=GOOGLE_API_KEY,
            temperature=TEMPERATURE,
            max_output_tokens=MAX_OUTPUT_TOKENS
        )
        
        # Initialize text splitter for handling large code bases
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=ANALYSIS_CHUNK_SIZE,
            chunk_overlap=ANALYSIS_CHUNK_OVERLAP
        )
    
    def generate_overview_document(self, output_dir: str) -> str:
        """Generate a high-level software overview document."""
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
        
        
        # Run the chain
        chain = overview_prompt | self.llm
        result = chain.invoke({
            "languages": json.dumps(languages, indent=2),
            "components": json.dumps(key_components, indent=2),
            "code_samples": code_samples_text
        })
        
        # Save result to file
        output_file = os.path.join(output_dir, "overview_doc.md")
        with open(output_file, 'w') as f:
            f.write(result)
        
        return output_file
    
    def generate_specification_document(self, output_dir: str) -> str:
        """Generate a detailed software specification document."""
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
        
        for i, doc in enumerate(chunked_documents[:10]):  # Limit to first 10 chunks for reasonable processing
            chain = component_prompt | self.llm
            result = chain.invoke({
                "file_path": doc.metadata["path"],
                "language": doc.metadata["language"],
                "code": doc.page_content
            })
            
            component_analyses.append(result)
        
        chain = integration_prompt | self.llm
        integration_section = chain.invoke({
            "components": "\n\n".join(component_analyses),
            "project_structure": json.dumps(self.code_analysis["project_structure"], indent=2)
        })
        
        # Combine all sections into the final specification document
        specification = f"""# Software Specification Document

## Table of Contents
1. [Component Specifications](#component-specifications)
2. [Integration Analysis](#integration-analysis)
3. [System Requirements](#system-requirements)
4. [Appendix](#appendix)

## Component Specifications

{(chr(10) + chr(10)).join(component_analyses)}

## Integration Analysis

{integration_section}

## Appendix

### Project Structure
```
{json.dumps(self.code_analysis["project_structure"], indent=2)}
```

### Technologies Used
```
{json.dumps(self.code_analysis["languages"], indent=2)}
```

*Document generated automatically from source code analysis*
"""
        
        # Save result to file
        output_file = os.path.join(output_dir, "spec_doc.md")
        with open(output_file, 'w') as f:
            f.write(specification)
        
        return output_file
    
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
