"""Utility decorators"""

import functools
import time
from typing import Any, Callable, Optional, Type, Union

from utils.logger import log, StructuredLogger

def retry(
    retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Union[Type[Exception], tuple] = Exception,
    logger: Optional[StructuredLogger] = None
):
    """Retry decorator with exponential backoff
    
    Args:
        retries: Maximum number of retries
        delay: Initial delay between retries in seconds
        backoff: Backoff multiplier
        exceptions: Exception(s) to catch
        logger: Logger instance
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            local_logger = logger or log
            current_delay = delay
            last_exception = None
            
            for attempt in range(retries + 1):
                try:
                    return func(*args, **kwargs)
                    
                except exceptions as e:
                    last_exception = e
                    if attempt == retries:
                        local_logger.error(
                            f"Failed after {retries} retries: {str(e)}"
                        )
                        raise
                    
                    local_logger.warning(
                        f"Attempt {attempt + 1}/{retries} failed: {str(e)}. "
                        f"Retrying in {current_delay:.1f}s..."
                    )
                    
                    time.sleep(current_delay)
                    current_delay *= backoff
            
            raise last_exception
            
        return wrapper
    return decorator 