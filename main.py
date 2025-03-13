import os
import argparse
from code_analyzer import CodeAnalyzer
from doc_generator import DocumentGenerator
from utils import setup_directories
from config import LANGSMITH_API_KEY, LANGSMITH_PROJECT, LANGSMITH_ENDPOINT, LANGSMITH_TRACING

def setup_langsmith():
    """Set up LangSmith tracing if API key is available."""
    if LANGSMITH_API_KEY:
        print(f"LangSmith tracing enabled:")
        print(f"  - Project: {LANGSMITH_PROJECT}")
        print(f"  - Endpoint: {LANGSMITH_ENDPOINT}")
        print(f"  - Tracing active: {LANGSMITH_TRACING}")
        
        # Set environment variables explicitly (some libraries look for these directly)
        os.environ["LANGCHAIN_API_KEY"] = LANGSMITH_API_KEY  # Backward compatibility
        os.environ["LANGSMITH_API_KEY"] = LANGSMITH_API_KEY
        os.environ["LANGCHAIN_PROJECT"] = LANGSMITH_PROJECT  # Backward compatibility
        os.environ["LANGSMITH_PROJECT"] = LANGSMITH_PROJECT
        os.environ["LANGCHAIN_TRACING_V2"] = str(LANGSMITH_TRACING).lower()  # Backward compatibility
        os.environ["LANGSMITH_TRACING"] = str(LANGSMITH_TRACING).lower()
        
        if LANGSMITH_ENDPOINT:
            os.environ["LANGCHAIN_ENDPOINT"] = LANGSMITH_ENDPOINT  # Backward compatibility
            os.environ["LANGSMITH_ENDPOINT"] = LANGSMITH_ENDPOINT
    else:
        print("LangSmith API key not found. Tracing disabled.")

def main():
    parser = argparse.ArgumentParser(description="Generate specification documents from source code")
    parser.add_argument("--source", "-s", help="Path to source code directory", default="source_code")
    parser.add_argument("--output", "-o", help="Output directory for generated docs", default="generated_docs")
    args = parser.parse_args()
    
    # Set up LangSmith for tracing
    setup_langsmith()
    
    # Set up directory structure
    setup_directories(args.output)
    
    # Analyze code
    analyzer = CodeAnalyzer(args.source)
    code_analysis = analyzer.analyze()
    
    # Generate documents
    doc_generator = DocumentGenerator(code_analysis)
    overview_file = doc_generator.generate_overview_document(args.output)
    spec_file = doc_generator.generate_specification_document(args.output)
    
    print(f"Documents generated successfully:")
    print(f"- Overview: {overview_file}")
    print(f"- Specification: {spec_file}")

if __name__ == "__main__": 
    main()
