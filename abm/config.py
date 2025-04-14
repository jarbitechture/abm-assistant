# abm/config.py

import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

def require_env(var_name: str, min_length: int = 1) -> str:
    """Gets an environment variable, raising an error if missing or too short."""
    value = os.getenv(var_name)
    if not value:
        logger.error(f"Missing required environment variable: {var_name}")
        raise EnvironmentError(f"Missing required environment variable: {var_name}")
    if min_length > 0 and len(value) < min_length:
        logger.error(f"Invalid value for {var_name}: Too short (len={len(value)}, required>={min_length})")
        raise ValueError(f"Invalid value for {var_name}: Too short (len={len(value)}, required>={min_length})")
    logger.debug(f"Loaded required environment variable: {var_name}")
    return value

def get_env_int(var_name: str, default: int) -> int:
    """Gets an environment variable as an integer, falling back to a default."""
    value_str = os.getenv(var_name)
    if value_str is None:
        logger.debug(f"Environment variable {var_name} not set. Using default: {default}")
        return default
    try:
        value_int = int(value_str)
        logger.debug(f"Loaded integer environment variable: {var_name}={value_int}")
        return value_int
    except ValueError:
        logger.warning(f"Invalid integer value for {var_name} ('{value_str}'). Using default: {default}")
        return default

def get_env_float(var_name: str, default: float) -> float:
    """Gets an environment variable as a float, falling back to a default."""
    value_str = os.getenv(var_name)
    if value_str is None:
        logger.debug(f"Environment variable {var_name} not set. Using default: {default}")
        return default
    try:
        value_float = float(value_str)
        logger.debug(f"Loaded float environment variable: {var_name}={value_float}")
        return value_float
    except ValueError:
        logger.warning(f"Invalid float value for {var_name} ('{value_str}'). Using default: {default}")
        return default

# --- Required API Keys ---
try:
    OPENAI_API_KEY = require_env("OPENAI_API_KEY", min_length=30)
    HUBSPOT_API_KEY = require_env("HUBSPOT_API_KEY", min_length=20)
    # Log success only if require_env doesn't raise an error
    logger.info("✅ Successfully loaded required API keys (OpenAI, HubSpot).")
except (EnvironmentError, ValueError) as e:
    # Errors are already logged in require_env, just re-raise or exit if critical
    # For simplicity here, we might let the program continue and fail later,
    # or you could raise a specific ConfigurationError or sys.exit()
    OPENAI_API_KEY = None # Set to None if loading failed
    HUBSPOT_API_KEY = None
    logger.critical(f"❌ Failed to load critical API keys: {e}. Application might not function correctly.")
    # raise e # Optional: uncomment to stop execution immediately


# --- Pipeline Configuration ---
TARGET_ACCOUNT_REVENUE_THRESHOLD = get_env_int("TARGET_ACCOUNT_REVENUE_THRESHOLD", 3000000)
# Optional pre-filter: Define if you still need it, otherwise remove
# PIPELINE_PRE_FILTER_REVENUE = get_env_int("PIPELINE_PRE_FILTER_REVENUE", 5000000)

# --- AI Model Configuration ---
OPENAI_SUMMARY_MODEL = os.getenv("OPENAI_SUMMARY_MODEL", "gpt-4")
CREWAI_LLM_MODEL = os.getenv("CREWAI_LLM_MODEL", "gpt-4-turbo")
CREWAI_LLM_TEMPERATURE = get_env_float("CREWAI_LLM_TEMPERATURE", 0.3)
logger.info(f"Using OpenAI Summary Model: {OPENAI_SUMMARY_MODEL}")
logger.info(f"Using CrewAI LLM Model: {CREWAI_LLM_MODEL} (Temp: {CREWAI_LLM_TEMPERATURE})")

# --- API Configuration (for Streamlit or other clients) ---
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
logger.info(f"API Base URL configured: {API_BASE_URL}")