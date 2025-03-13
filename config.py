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
