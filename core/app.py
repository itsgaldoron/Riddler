"""Core application with resource management."""

import time
import multiprocessing as mp
import psutil
from pathlib import Path
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
from utils.logger import log
from utils.metrics import metrics
from utils.helpers import ensure_directory
from config.exceptions import RiddlerException

class RiddleApp:
    """Main application class with resource management."""
    
    def __init__(
        self,
        output_dir: str = "output",
        cache_dir: str = "cache",
        config_path: str = "config/config.json",
        max_workers: Optional[int] = None,
        max_memory_percent: float = 80.0,
        max_cpu_percent: float = 90.0
    ):
        """Initialize riddle app with resource limits.
        
        Args:
            output_dir: Output directory
            cache_dir: Cache directory
            config_path: Configuration file path
            max_workers: Maximum number of workers
            max_memory_percent: Maximum memory usage percentage
            max_cpu_percent: Maximum CPU usage percentage
        """
        self.output_dir = Path(output_dir)
        self.cache_dir = Path(cache_dir)
        self.config_path = Path(config_path)
        
        # Resource limits
        self.max_memory_percent = max_memory_percent
        self.max_cpu_percent = max_cpu_percent
        
        # Create directories
        ensure_directory(self.output_dir)
        ensure_directory(self.cache_dir)
        
        # Load config
        self.config = self._load_config()
        
        # Initialize thread pool with dynamic sizing
        self.max_workers = self._calculate_optimal_workers(max_workers)
        self.thread_pool = ThreadPoolExecutor(
            max_workers=self.max_workers,
            thread_name_prefix="riddler"
        )

    def _calculate_optimal_workers(
        self,
        max_workers: Optional[int] = None
    ) -> int:
        """Calculate optimal number of workers based on system resources.
        
        Args:
            max_workers: Maximum number of workers override
            
        Returns:
            Optimal number of workers
        """
        if max_workers is not None:
            return max_workers
            
        # Get system resources
        cpu_count = mp.cpu_count()
        memory = psutil.virtual_memory()
        
        # Calculate based on CPU and memory
        cpu_workers = max(1, cpu_count - 1)  # Leave one core free
        memory_workers = max(1, int(
            (memory.total * (self.max_memory_percent / 100)) /
            (500 * 1024 * 1024)  # Assume 500MB per worker
        ))
        
        return min(cpu_workers, memory_workers)

    def _check_resources(self) -> bool:
        """Check if system resources are available.
        
        Returns:
            Whether resources are available
        """
        try:
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent
            
            return (
                cpu_percent < self.max_cpu_percent and
                memory_percent < self.max_memory_percent
            )
        except Exception:
            return True  # Default to true if monitoring fails

    def batch_generate(
        self,
        categories: List[str],
        count_per_category: int = 1,
        **kwargs
    ) -> List[Path]:
        """Generate multiple riddle videos with improved resource management.
        
        Args:
            categories: List of categories
            count_per_category: Number of videos per category
            **kwargs: Additional arguments for video generation
            
        Returns:
            List of paths to generated videos
        """
        start_time = time.time()
        success = True
        videos = []
        
        try:
            # Create generation tasks
            tasks = []
            for category in categories:
                for _ in range(count_per_category):
                    tasks.append((category, kwargs))
                    
            # Process tasks with resource management
            futures = []
            pending_tasks = tasks.copy()
            
            while pending_tasks:
                # Check resources
                if not self._check_resources():
                    log.warning("System resources low, waiting...")
                    time.sleep(5)
                    continue
                    
                # Submit new tasks if resources available
                while pending_tasks and len(futures) < self.max_workers:
                    category, kwargs = pending_tasks.pop(0)
                    future = self.thread_pool.submit(
                        self.generate_video,
                        category=category,
                        **kwargs
                    )
                    futures.append(future)
                    
                # Check completed tasks
                done, futures = concurrent.futures.wait(
                    futures,
                    timeout=1,
                    return_when=concurrent.futures.FIRST_COMPLETED
                )
                
                for future in done:
                    try:
                        video_path = future.result()
                        videos.append(video_path)
                    except Exception as e:
                        log.error(f"Failed to generate video: {e}")
                        success = False
                        
            # Record metrics
            duration = time.time() - start_time
            metrics.record_request(
                "batch_video",
                duration,
                success=success
            )
            
            return videos
            
        except Exception as e:
            # Record failure metrics
            duration = time.time() - start_time
            metrics.record_request(
                "batch_video",
                duration,
                success=False
            )
            
            raise RiddlerException(f"Failed to generate videos: {str(e)}")

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file.
        
        Returns:
            Configuration dictionary
        """
        try:
            import json
            return json.loads(self.config_path.read_text())
        except Exception as e:
            raise RiddlerException(f"Failed to load config: {str(e)}")

    def generate_video(
        self,
        category: str,
        **kwargs
    ) -> Path:
        """Generate a single riddle video.
        
        Args:
            category: Riddle category
            **kwargs: Additional arguments for video generation
            
        Returns:
            Path to generated video
        """
        try:
            # Initialize services if needed
            if not hasattr(self, 'video_service'):
                from services.video import VideoService
                self.video_service = VideoService(
                    output_dir=self.output_dir,
                    height=1920
                )
                
            if not hasattr(self, 'riddle_service'):
                from services.riddle import RiddleService
                self.riddle_service = RiddleService()
                
            # Generate riddle content
            riddle_data = self.riddle_service.generate_riddle(category)
            
            # Generate video
            return self.video_service.generate_riddle_video(
                riddle_text=riddle_data['riddle'],
                answer_text=riddle_data['answer'],
                **kwargs
            )
            
        except Exception as e:
            raise RiddlerException(f"Failed to generate video: {str(e)}")

# Initialize global app instance
app = RiddleApp() 