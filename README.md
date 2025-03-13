# Specification Document Generator

This tool automatically generates software specification documents from source code using Google's Gemini LLM.

## Features

- Source code analysis
- Software overview document generation
- Detailed specification document generation
- Support for multiple programming languages

## Setup

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your Google API key:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```

## Usage

Run the tool with:

```bash
python main.py --source /path/to/source/code --output /path/to/output
```

This will analyze the source code and generate:
- `software_overview.md`: High-level overview of the system
- `software_specification.md`: Detailed specification document

## Requirements

- Python 3.8+
- Google API key with access to Gemini models
