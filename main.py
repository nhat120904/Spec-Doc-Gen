import os
import argparse
from code_analyzer import CodeAnalyzer
from doc_generator import DocumentGenerator
from utils import setup_directories

def main():
    parser = argparse.ArgumentParser(description="Generate specification documents from source code")
    parser.add_argument("--source", "-s", help="Path to source code directory", default="source_code")
    parser.add_argument("--output", "-o", help="Output directory for generated docs", default="generated_docs")
    args = parser.parse_args()
    
    # Set up directory structure
    setup_directories(args.output)
    
    # Analyze code
    analyzer = CodeAnalyzer(args.source)
    code_analysis = analyzer.analyze()
    
    # Generate documents
    doc_generator = DocumentGenerator(code_analysis)
    doc_generator.generate_overview_document(args.output)
    doc_generator.generate_specification_document(args.output)
    
    print(f"Documents generated successfully in {args.output}")

if __name__ == "__main__":
    main()
