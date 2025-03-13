import os
import re
from typing import List, Dict, Any

def setup_directories(output_dir: str):
    """Create necessary directories if they don't exist."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

def extract_file_extension(filename: str) -> str:
    """Extract file extension from filename."""
    return os.path.splitext(filename)[1][1:]

def detect_programming_language(file_extension: str) -> str:
    """Detect programming language from file extension."""
    language_map = {
        'py': 'Python',
        'js': 'JavaScript',
        'ts': 'TypeScript',
        'java': 'Java',
        'cpp': 'C++',
        'c': 'C',
        'cs': 'C#',
        'go': 'Go',
        'rb': 'Ruby',
        'php': 'PHP',
        'rs': 'Rust',
        'swift': 'Swift',
        'kt': 'Kotlin',
        'scala': 'Scala',
    }
    return language_map.get(file_extension.lower(), 'Unknown')

def clean_code_for_llm(code_content: str) -> str:
    """Clean code and prepare it for LLM analysis."""
    # Remove redundant comments or line numbers if needed
    # Normalize whitespace
    return code_content.strip()
