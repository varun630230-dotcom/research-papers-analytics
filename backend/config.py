"""
ResearchGap AI - Configuration Module
======================================
Loads environment variables from .env file and provides
application-wide settings as a simple dictionary.

Why a simple dictionary instead of a Settings class?
- Easier to understand for beginners
- No need for pydantic-settings dependency
- All config values in one visible place
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file (checks root, backend/, or cwd)
root_env = os.path.join(os.path.dirname(__file__), "..", ".env")
backend_env = os.path.join(os.path.dirname(__file__), ".env")

if os.path.exists(root_env):
    load_dotenv(dotenv_path=root_env)
elif os.path.exists(backend_env):
    load_dotenv(dotenv_path=backend_env)
else:
    load_dotenv()


def get_config():
    """
    Returns a dictionary with all application configuration.
    
    Values come from environment variables with sensible defaults.
    API keys have no defaults — they must be set in .env file.
    """
    return {
        # --- API Keys ---
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY", ""),
        "OPENALEX_EMAIL": os.getenv("OPENALEX_EMAIL", ""),
        "SEMANTIC_SCHOLAR_API_KEY": os.getenv("SEMANTIC_SCHOLAR_API_KEY", ""),
        
        # --- Gemini Settings ---
        "GEMINI_MODEL": "gemini-2.0-flash",
        "GEMINI_BASE_URL": "https://generativelanguage.googleapis.com/v1beta",
        
        # --- Server Settings ---
        "HOST": os.getenv("HOST", "127.0.0.1"),
        "PORT": int(os.getenv("PORT", "8000")),
        
        # --- Database ---
        # Path to SQLite database file (relative to project root)
        "DATABASE_PATH": os.path.join(
            os.path.dirname(__file__), "..", "data", "research.db"
        ),
        
        # --- Academic API Settings ---
        # Maximum papers to fetch from each source
        "PAPERS_PER_SOURCE": 15,
        # Maximum total papers after filtering
        "MAX_PAPERS_TOTAL": 40,
        # Request timeout in seconds
        "API_TIMEOUT": 30,
        
        # --- PDF Settings ---
        # Maximum PDF file size to download (in bytes, 10 MB)
        "MAX_PDF_SIZE": 10 * 1024 * 1024,
        # Maximum text characters to send to Gemini per paper
        "MAX_TEXT_LENGTH": 15000,
        
        # --- CORS ---
        # Origins allowed to make requests to our API
        "CORS_ORIGINS": ["http://localhost:8000", "http://127.0.0.1:8000"],
    }


# Create a module-level config object so other files can import it directly
# Usage: from config import config
#        api_key = config["GEMINI_API_KEY"]
config = get_config()


def validate_config():
    """
    Checks that required configuration values are present.
    Returns a list of missing/invalid items. Empty list = all good.
    """
    issues = []
    
    if not config["GEMINI_API_KEY"]:
        issues.append(
            "GEMINI_API_KEY is not set. "
            "Get a free key at https://makersuite.google.com/app/apikey "
            "and add it to your .env file."
        )
    
    return issues
