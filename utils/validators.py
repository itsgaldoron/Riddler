"""Input validation utilities"""

import os
from typing import List
from config.config import Configuration as Config

def validate_category(category: str) -> bool:
    """Validate riddle category
    
    Args:
        category: Category to validate
        
    Returns:
        True if valid
        
    Raises:
        ValueError: If category is invalid
    """
    config = Config()
    video_config = config.get("video", {})
    pexels_config = video_config.get("pexels", {})
    category_terms = pexels_config.get("category_terms", {})
    valid_categories = list(category_terms.keys())
    
    if not category or category not in valid_categories:
        raise ValueError(
            f"Invalid category: {category}. "
            f"Must be one of: {', '.join(valid_categories)}"
        )
    
    return True

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