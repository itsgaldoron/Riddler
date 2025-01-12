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
    """Get API key from environment variables."""
    load_dotenv()  # Reload environment variables from .env file
    
    key_map = {
        "openai": "RIDDLER_OPENAI_API_KEY",
        "elevenlabs": "RIDDLER_ELEVENLABS_API_KEY",
        "pexels": "RIDDLER_PEXELS_API_KEY"
    }
    
    env_var = key_map.get(service.lower())
    if not env_var:
        raise ValueError(f"Unknown service: {service}")
        
    api_key = os.getenv(env_var)
    if not api_key:
        raise ValueError(f"API key not found for {service}")
        
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

def get_resource_path(resource_type: str, *paths: str) -> str:
    """Get the absolute path to a package resource.
    
    Args:
        resource_type: Type of resource ('assets', 'config', etc.)
        *paths: Additional path components
        
    Returns:
        Absolute path to the resource
    """
    resources_dir = os.path.join(os.path.dirname(__file__), "..", "resources")
    return os.path.join(resources_dir, resource_type, *paths)

