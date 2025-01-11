"""Helper utilities"""

import hashlib
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import time
from datetime import datetime
import re
from dotenv import load_dotenv
from .logger import log

def reload_env() -> None:
    """Reload environment variables from .env file."""
    load_dotenv(override=True)

def get_api_key(service: str) -> str:
    """Get API key for a service from environment variables.
    
    Args:
        service: Service name (e.g., 'openai', 'elevenlabs')
        
    Returns:
        API key for the service
        
    Raises:
        ValueError: If API key is not found
    """
    # Reload environment variables
    reload_env()
    
    env_var = f"RIDDLER_{service.upper()}_API_KEY"
    api_key = os.getenv(env_var)
    
    if not api_key:
        raise ValueError(f"API key not found for {service} (env var: {env_var})")
        
    return api_key

def ensure_directory(path: Union[str, Path]) -> Path:
    """Ensure a directory exists and create it if it doesn't.
    
    Args:
        path: Directory path to ensure exists
        
    Returns:
        Path object of the ensured directory
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path

