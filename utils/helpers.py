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

def get_cache_key(prefix: str, **kwargs: Any) -> str:
    """Generate a cache key from prefix and parameters.
    
    Args:
        prefix: Prefix for the cache key
        **kwargs: Parameters to include in key generation
        
    Returns:
        Generated cache key
    """
    # Sort kwargs to ensure consistent key generation
    sorted_items = sorted(kwargs.items())
    
    # Create string representation of parameters
    params_str = json.dumps(sorted_items, sort_keys=True)
    
    # Generate hash
    key_hash = hashlib.md5(params_str.encode()).hexdigest()
    
    return f"{prefix}_{key_hash}"

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

def generate_cache_key(prefix: str, **kwargs: Any) -> str:
    """Generate a cache key from prefix and parameters.
    
    Args:
        prefix: Prefix for the cache key
        **kwargs: Parameters to include in key generation
        
    Returns:
        Generated cache key
    """
    # Sort kwargs to ensure consistent key generation
    sorted_items = sorted(kwargs.items())
    
    # Create string representation of parameters
    params_str = json.dumps(sorted_items, sort_keys=True)
    
    # Generate hash
    key_hash = hashlib.md5(params_str.encode()).hexdigest()
    
    return f"{prefix}_{key_hash}"

def retry_with_backoff(
    func: callable,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 10.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
) -> Any:
    """Retry a function with exponential backoff.
    
    Args:
        func: Function to retry
        max_retries: Maximum number of retries
        initial_delay: Initial delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        backoff_factor: Factor to multiply delay by after each retry
        exceptions: Tuple of exceptions to catch
        
    Returns:
        Result of the function call
        
    Raises:
        The last exception encountered if all retries fail
    """
    delay = initial_delay
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            return func()
        except exceptions as e:
            last_exception = e
            if attempt == max_retries - 1:
                raise
                
            log.warning(
                f"Attempt {attempt + 1}/{max_retries} failed",
                extra={
                    "error": str(e),
                    "delay": delay,
                    "function": func.__name__
                }
            )
            
            time.sleep(delay)
            delay = min(delay * backoff_factor, max_delay)
            
    if last_exception:
        raise last_exception

def sanitize_filename(filename: str) -> str:
    """Sanitize a filename to be safe for all operating systems.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    
    # Remove control characters
    filename = "".join(char for char in filename if ord(char) >= 32)
    
    # Trim whitespace and periods
    filename = filename.strip(". ")
    
    # Ensure filename is not empty
    if not filename:
        filename = "unnamed"
        
    return filename

def format_timestamp(seconds: float) -> str:
    """Format seconds into HH:MM:SS.mmm format.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted timestamp string
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"

def parse_timestamp(timestamp: str) -> float:
    """Parse HH:MM:SS.mmm format into seconds.
    
    Args:
        timestamp: Timestamp string
        
    Returns:
        Time in seconds
    """
    pattern = r"^(\d+):(\d{2}):(\d{2}(?:\.\d+)?)$"
    match = re.match(pattern, timestamp)
    
    if not match:
        raise ValueError(f"Invalid timestamp format: {timestamp}")
        
    hours, minutes, seconds = match.groups()
    total_seconds = int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    
    return total_seconds

def chunk_text(
    text: str,
    max_length: int,
    separator: str = " "
) -> List[str]:
    """Split text into chunks of maximum length.
    
    Args:
        text: Text to split
        max_length: Maximum length of each chunk
        separator: Separator to split on
        
    Returns:
        List of text chunks
    """
    chunks = []
    current_chunk = []
    current_length = 0
    
    for word in text.split(separator):
        word_length = len(word)
        
        if current_length + word_length + 1 <= max_length:
            current_chunk.append(word)
            current_length += word_length + 1
        else:
            if current_chunk:
                chunks.append(separator.join(current_chunk))
            current_chunk = [word]
            current_length = word_length
            
    if current_chunk:
        chunks.append(separator.join(current_chunk))
        
    return chunks

def deep_merge(
    dict1: Dict[str, Any],
    dict2: Dict[str, Any]
) -> Dict[str, Any]:
    """Deep merge two dictionaries.
    
    Args:
        dict1: First dictionary
        dict2: Second dictionary
        
    Returns:
        Merged dictionary
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if (
            key in result and
            isinstance(result[key], dict) and
            isinstance(value, dict)
        ):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
            
    return result 