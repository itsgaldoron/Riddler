"""Input validation utilities"""

import os
from typing import List

def validate_category(category: str) -> bool:
    """Validate riddle category
    
    Args:
        category: Category to validate
        
    Returns:
        True if valid
        
    Raises:
        ValueError: If category is invalid
    """
    valid_categories = [
        "geography",
        "math",
        "physics",
        "history",
        "logic",
        "wordplay"
    ]
    
    if not category or category not in valid_categories:
        raise ValueError(
            f"Invalid category: {category}. "
            f"Must be one of: {', '.join(valid_categories)}"
        )
    
    return True

def validate_difficulty(difficulty: str) -> bool:
    """Validate difficulty level
    
    Args:
        difficulty: Difficulty level to validate
        
    Returns:
        True if valid
        
    Raises:
        ValueError: If difficulty is invalid
    """
    valid_difficulties = ["easy", "medium", "hard"]
    
    if not difficulty or difficulty not in valid_difficulties:
        raise ValueError(
            f"Invalid difficulty: {difficulty}. "
            f"Must be one of: {', '.join(valid_difficulties)}"
        )
    
    return True

def validate_duration(duration: int) -> bool:
    """Validate video duration
    
    Args:
        duration: Duration in seconds
        
    Returns:
        True if valid
        
    Raises:
        ValueError: If duration is invalid
    """
    min_duration = 30
    max_duration = 60
    
    if not isinstance(duration, int):
        raise ValueError("Duration must be an integer")
    
    if duration < min_duration or duration > max_duration:
        raise ValueError(
            f"Invalid duration: {duration}. "
            f"Must be between {min_duration} and {max_duration} seconds"
        )
    
    return True

def validate_api_key(key_name: str, key_value: str) -> bool:
    """Validate API key
    
    Args:
        key_name: Name of the API key
        key_value: Value of the API key
        
    Returns:
        True if valid
        
    Raises:
        ValueError: If API key is invalid
    """
    valid_key_names = [
        "RIDDLER_PEXELS_API_KEY",
        "RIDDLER_ELEVENLABS_API_KEY",
        "RIDDLER_OPENAI_API_KEY"
    ]
    
    if not key_name or key_name not in valid_key_names:
        raise ValueError(
            f"Invalid API key name: {key_name}. "
            f"Must be one of: {', '.join(valid_key_names)}"
        )
    
    if not key_value:
        raise ValueError(f"API key not found: {key_name}")
    
    return True

def validate_file_path(file_path: str) -> bool:
    """Validate file path
    
    Args:
        file_path: Path to validate
        
    Returns:
        True if valid
        
    Raises:
        ValueError: If path is invalid
    """
    if not file_path:
        raise ValueError("File path cannot be empty")
    
    if not os.path.exists(file_path):
        raise ValueError(f"File not found: {file_path}")
    
    return True

def validate_cache_dir(cache_dir: str) -> bool:
    """Validate cache directory
    
    Args:
        cache_dir: Directory to validate
        
    Returns:
        True if valid
        
    Raises:
        ValueError: If directory is invalid
    """
    if not cache_dir:
        raise ValueError("Cache directory cannot be empty")
    
    if not os.path.isdir(cache_dir):
        raise ValueError(f"Not a directory: {cache_dir}")
    
    # Check write permissions
    try:
        test_file = os.path.join(cache_dir, ".test")
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
    except (IOError, OSError):
        raise ValueError(f"No write permission: {cache_dir}")
    
    return True 