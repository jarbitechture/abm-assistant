# abm/config.py

import os
from dotenv import load_dotenv

load_dotenv()

def require_env(var_name: str, min_length: int = 10) -> str:
    value = os.getenv(var_name)
    if not value:
        raise EnvironmentError(f"Missing required environment variable: {var_name}")
    if len(value) < min_length:
        raise ValueError(f"Invalid value for {var_name}: Too short (len={len(value)})")
    return value

# Required environment variables
OPENAI_API_KEY = require_env("OPENAI_API_KEY", min_length=30)
HUBSPOT_API_KEY = require_env("HUBSPOT_API_KEY", min_length=20)
