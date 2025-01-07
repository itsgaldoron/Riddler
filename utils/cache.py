"""Cache management utilities"""

import hashlib
import pickle
import zlib
from pathlib import Path
from typing import Any, Dict, Optional
from concurrent.futures import ThreadPoolExecutor
from utils.logger import log

class CacheManager:
    """Manages caching of data with compression and organization."""
    
    def __init__(
        self,
        base_dir: str = "cache",
        intermediate_dir: str = "cache/intermediate",
        max_size: int = 10 * 1024 * 1024 * 1024,  # 10GB
        cleanup_threshold: float = 0.9,
        max_workers: int = 4
    ):
        """Initialize cache manager.
        
        Args:
            base_dir: Base cache directory
            intermediate_dir: Directory for intermediate results
            max_size: Maximum cache size in bytes
            cleanup_threshold: Cleanup threshold (0-1)
            max_workers: Maximum number of worker threads
        """
        self.base_dir = Path(base_dir)
        self.intermediate_dir = Path(intermediate_dir)
        self.max_size = max_size
        self.cleanup_threshold = cleanup_threshold
        
        # Create directories
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.intermediate_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize executor for async operations
        self.executor = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="cache"
        )
        
        # Initialize stats
        self.stats = CacheStats()
        
    @property
    def cache_dir(self) -> str:
        """Get the cache directory path.
        
        Returns:
            Cache directory path as string
        """
        return str(self.base_dir)

    def _load_stats(self) -> None:
        """Load cache statistics from disk or initialize new ones."""
        stats_path = self.base_dir / "stats.pkl"
        try:
            if stats_path.exists():
                with open(stats_path, "rb") as f:
                    self.stats = pickle.load(f)
            else:
                self.stats = CacheStats()
        except Exception as e:
            log.warning(f"Failed to load cache stats: {e}")
            self.stats = CacheStats()

    def _update_stats(self, hit: bool = False, size_delta: int = 0) -> None:
        """Update cache statistics.
        
        Args:
            hit: Whether this was a cache hit
            size_delta: Change in cache size
        """
        if hit:
            self.stats.hits += 1
        else:
            self.stats.misses += 1
        self.stats.size_bytes += size_delta
        
        # Save stats periodically
        stats_path = self.base_dir / "stats.pkl"
        try:
            with open(stats_path, "wb") as f:
                pickle.dump(self.stats, f)
        except Exception as e:
            log.warning(f"Failed to save cache stats: {e}")

    def _get_cache_path(self, key: str, intermediate: bool = False, extension: str = '.mp4') -> Path:
        """Get cache file path with improved organization.
        
        Args:
            key: Cache key
            intermediate: Whether this is an intermediate result
            extension: File extension to use (defaults to .mp4)
            
        Returns:
            Cache file path
        """
        # Use first 2 chars of hash for subdirectory to prevent too many files in one dir
        filename = hashlib.sha256(key.encode()).hexdigest()
        subdir = filename[:2]
        
        if intermediate:
            path = self.intermediate_dir / subdir
        else:
            path = self.base_dir / subdir
            
        path.mkdir(exist_ok=True)
        return path / f"{filename[2:]}{extension}"

    def put(
        self,
        key: str,
        data: Any,
        intermediate: bool = False,
        compression_level: Optional[int] = None
    ) -> bool:
        """Put item in cache with compression.
        
        Args:
            key: Cache key
            data: Data to cache
            intermediate: Whether this is an intermediate result
            compression_level: Optional compression level (0-9)
            
        Returns:
            Whether operation was successful
        """
        if self._should_cleanup():
            self.executor.submit(self.cleanup)
            
        # Determine extension based on data type
        extension = '.mp4'  # default
        if isinstance(data, str):
            if data.endswith('.mp3'):
                extension = '.mp3'
            elif data.endswith('.wav'):
                extension = '.wav'
                
        path = self._get_cache_path(key, intermediate, extension)
        
        try:
            # If data is a string and ends with .mp4, it's a video file path
            if isinstance(data, str) and data.endswith('.mp4'):
                # Copy the video file to the cache location
                import shutil
                shutil.copy2(data, path)
                size = path.stat().st_size
            else:
                # Serialize data using pickle
                serialized_data = pickle.dumps(data, protocol=pickle.HIGHEST_PROTOCOL)
                
                if compression_level is not None:
                    serialized_data = zlib.compress(serialized_data, level=compression_level)
                    
                path.write_bytes(serialized_data)
                size = path.stat().st_size
                
            self._update_stats(size_delta=size)
            self.stats.items_count += 1
            
            return True
            
        except Exception as e:
            log.warning(f"Failed to write cache item {key}: {e}")
            return False

    def get(
        self,
        key: str,
        intermediate: bool = False
    ) -> Optional[Any]:
        """Get item from cache with decompression support.
        
        Args:
            key: Cache key
            intermediate: Whether this is an intermediate result
            
        Returns:
            Cached item or None if not found
        """
        path = self._get_cache_path(key, intermediate)
        
        if not path.exists():
            self._update_stats(hit=False)
            return None
            
        try:
            # If it's a video file, return the path
            if path.suffix == '.mp4':
                self._update_stats(hit=True)
                return str(path)
                
            # Otherwise, try to deserialize the data
            data = path.read_bytes()
            try:
                # Try to decompress if compressed
                data = zlib.decompress(data)
            except zlib.error:
                # Not compressed, continue with deserialization
                pass
                
            # Deserialize the data
            data = pickle.loads(data)
            self._update_stats(hit=True)
            return data
            
        except Exception as e:
            log.warning(f"Failed to read cache item {key}: {e}")
            self._update_stats(hit=False)
            return None

    def _should_cleanup(self) -> bool:
        """Check if cleanup is needed.
        
        Returns:
            Whether cleanup is needed
        """
        total_size = sum(
            f.stat().st_size
            for f in self.base_dir.rglob("*")
            if f.is_file()
        )
        return total_size > self.max_size * self.cleanup_threshold

    def cleanup(self) -> None:
        """Clean up old cache files."""
        try:
            # Get all cache files with their timestamps
            files = []
            for path in self.base_dir.rglob("*"):
                if path.is_file():
                    files.append((path, path.stat().st_mtime))
                    
            # Sort by timestamp (oldest first)
            files.sort(key=lambda x: x[1])
            
            # Calculate total size
            total_size = sum(path.stat().st_size for path, _ in files)
            
            # Remove files until under threshold
            for path, _ in files:
                if total_size <= self.max_size * 0.8:  # Keep 20% buffer
                    break
                    
                try:
                    size = path.stat().st_size
                    path.unlink()
                    total_size -= size
                except Exception as e:
                    log.warning(f"Failed to remove cache file {path}: {e}")
                    
        except Exception as e:
            log.error(f"Failed to clean cache: {e}")

class CacheStats:
    """Cache statistics."""
    
    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.size_bytes = 0
        self.items_count = 0
        
    @property
    def hit_rate(self) -> float:
        """Calculate cache hit rate.
        
        Returns:
            Hit rate (0-1)
        """
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0

# Initialize global cache instance
cache = CacheManager() 