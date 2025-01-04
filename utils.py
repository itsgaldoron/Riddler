import sys
from typing import Iterator, List, Any, Callable
from concurrent.futures import ProcessPoolExecutor, as_completed
from config import PROGRESS, PARALLEL
import time

class ProgressBar:
    """A simple progress bar for tracking long operations."""
    
    def __init__(self, total: int, desc: str = ""):
        """
        Initialize the progress bar.
        
        Args:
            total: Total number of items
            desc: Description of the operation
        """
        self.total = total
        self.current = 0
        self.desc = desc
        self.start_time = time.time()
        self._print_progress()
    
    def update(self, n: int = 1) -> None:
        """Update the progress bar."""
        self.current += n
        self._print_progress()
    
    def _print_progress(self) -> None:
        """Print the progress bar to the console."""
        percentage = int(100 * self.current / self.total)
        filled = int(PROGRESS['width'] * self.current / self.total)
        bar = PROGRESS['fill'] * filled + PROGRESS['empty'] * (PROGRESS['width'] - filled)
        
        # Calculate elapsed time and ETA
        elapsed = time.time() - self.start_time
        if self.current > 0:
            eta = elapsed * (self.total / self.current - 1)
            time_info = f" | {format_time(elapsed)} < {format_time(eta)}"
        else:
            time_info = ""
        
        print(
            f"\r{PROGRESS['format'].format(bar=bar, percentage=percentage, desc=self.desc)}{time_info}",
            end="",
            file=sys.stderr
        )
        
        if self.current >= self.total:
            print(file=sys.stderr)  # New line when complete
    
    def __enter__(self):
        """Context manager enter."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if exc_type is None:
            self.current = self.total
            self._print_progress()

def format_time(seconds: float) -> str:
    """Format time in seconds to a human-readable string."""
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    if hours > 0:
        return f"{hours}h{minutes:02d}m{seconds:02d}s"
    elif minutes > 0:
        return f"{minutes}m{seconds:02d}s"
    else:
        return f"{seconds}s"

def process_in_parallel(
    items: List[Any],
    process_func: Callable,
    desc: str = "",
    max_workers: int = PARALLEL['max_workers']
) -> List[Any]:
    """
    Process items in parallel with a progress bar.
    
    Args:
        items: List of items to process
        process_func: Function to process each item
        desc: Description for the progress bar
        max_workers: Maximum number of parallel workers
    
    Returns:
        List of processed items
    """
    results = []
    with ProgressBar(len(items), desc=desc) as pbar:
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(process_func, item) for item in items]
            for future in as_completed(futures):
                results.append(future.result())
                pbar.update()
    return results

def chunk_list(lst: List[Any], chunk_size: int) -> Iterator[List[Any]]:
    """Split a list into chunks of specified size."""
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size] 