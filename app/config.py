import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class AppConfig:
    """
    Configuration class for the application.
    Reads values from environment variables.
    """
    
    def __init__(self):
        # Setting up logging
        logging.basicConfig(level=self._get_logging_level())
        self.logger = logging.getLogger(__name__)
        
        # Core settings
        self.llm_api_key = os.getenv("LLM_API_KEY")
        if not self.llm_api_key:
            self.logger.warning("LLM_API_KEY not set in environment variables")
        
        self.default_llm_provider = os.getenv("DEFAULT_LLM_PROVIDER", "openai")
        self.default_model = os.getenv("DEFAULT_MODEL", "gpt-3.5-turbo")
        
    def _get_logging_level(self):
        """Get the logging level from environment or default to INFO"""
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        return getattr(logging, log_level, logging.INFO)

def load_config():
    """Helper function to load and return a dictionary of config values"""
    return {
        "LLM_API_KEY": os.getenv("LLM_API_KEY"),
        "LLM_MODEL": os.getenv("LLM_MODEL", "gpt-3.5-turbo"),
        "LLM_PROVIDER": os.getenv("LLM_PROVIDER", "openai"),
        "SYSTEM_PROMPT_PATH": os.getenv("SYSTEM_PROMPT_PATH", "prompts/entity_extraction.txt"),
        "MAX_TOKENS": int(os.getenv("MAX_TOKENS", "100")),
        "TEMPERATURE": float(os.getenv("TEMPERATURE", "0.0")),
        "DBPEDIA_GRAPH_LOCATION": os.getenv("DBPEDIA_GRAPH_LOCATION", "./data/dbpedia")
    }
