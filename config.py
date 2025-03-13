import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Google API key for Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Default directories/paths
DEFAULT_SOURCE_DIR = "source_code"
OUTPUT_DIR = "generated_docs"

# LLM Configuration
MODEL_NAME = "gemini-2.0-flash-exp"
TEMPERATURE = 0.2
MAX_OUTPUT_TOKENS = 4096

# Document generation settings
ANALYSIS_CHUNK_SIZE = 4000
ANALYSIS_CHUNK_OVERLAP = 200

# LangSmith Configuration - updated variable names
LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING", "true").lower() == "true"
LANGSMITH_ENDPOINT = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY", "")
LANGSMITH_PROJECT = os.getenv("LANGSMITH_PROJECT", "spec-doc-generator")

# Keep backward compatibility
LANGCHAIN_TRACING_V2 = LANGSMITH_TRACING
LANGCHAIN_ENDPOINT = LANGSMITH_ENDPOINT
LANGCHAIN_API_KEY = LANGSMITH_API_KEY
LANGCHAIN_PROJECT = LANGSMITH_PROJECT
