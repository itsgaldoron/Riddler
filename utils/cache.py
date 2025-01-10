"""Cache management utilities"""

import hashlib
import pickle
import zlib
from pathlib import Path
from typing import Any, Optional
from concurrent.futures import ThreadPoolExecutor
from utils.logger import log
from config.config import Configuration as Config

class CacheManager:
    """Manages caching of data with compression and organization."""
    
    def __init__(
        self,
        base_dir: str = "cache",
        max_size: Optional[int] = None,
        cleanup_threshold: Optional[float] = None,
        max_workers: int = 4
    ):
        """Initialize cache manager.
        
        Args:
            base_dir: Base cache directory
            max_size: Maximum cache size in bytes
            cleanup_threshold: Cleanup threshold (0-1)
            max_workers: Maximum number of worker threads
        """
        self.config = Config()
        self.base_dir = Path(base_dir)
        
        # Use config values or defaults
        self.max_size = max_size or self.config.get("cache.max_cache_size", 10 * 1024 * 1024 * 1024)  # Default 10GB
        self.cleanup_threshold = cleanup_threshold or self.config.get("cache.cleanup_threshold", 0.9)
        
        # Create directory
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize executor for async operations
        self.executor = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="cache"
        )
        
        # Initialize stats
        self.stats = CacheStats()
        
    @property
    def cache_dir(self) -> str:
        """Get the cache directory path."""
        return str(self.base_dir)

    def _update_stats(self, hit: bool = False, size_delta: int = 0) -> None:
        """Update cache statistics."""
        if hit:
            self.stats.hits += 1
        else:
            self.stats.misses += 1
        self.stats.size_bytes += size_delta
        
        # Save stats
        stats_path = self.base_dir / "stats.pkl"
        try:
            with open(stats_path, "wb") as f:
                pickle.dump(self.stats, f)
        except Exception as e:
            log.warning(f"Failed to save cache stats: {e}")

    def _get_cache_path(self, key: str, extension: str = None) -> Path:
        """Get cache file path.
        
        Args:
            key: Cache key
            extension: Optional file extension (defaults to .pkl)
            
        Returns:
            Cache file path
        """
        filename = hashlib.sha256(key.encode()).hexdigest()
        subdir = filename[:2]
        path = self.base_dir / subdir
        path.mkdir(exist_ok=True)
        
        # Use provided extension or default to .pkl for serialized data
        ext = extension or '.pkl'
        return path / f"{filename[2:]}{ext}"

    def put(
        self,
        key: str,
        data: Any,
        compression_level: Optional[int] = None
    ) -> bool:
        """Put item in cache with compression.
        
        Args:
            key: Cache key
            data: Data to cache
            compression_level: Optional compression level (0-9)
            
        Returns:
            Whether operation was successful
        """
        if self._should_cleanup():
            self.executor.submit(self.cleanup)
            
        try:
            # Handle media files (copy to cache)
            if isinstance(data, str) and any(data.endswith(ext) for ext in ['.mp4', '.mp3', '.wav']):
                extension = Path(data).suffix
                path = self._get_cache_path(key, extension)
                import shutil
                shutil.copy2(data, path)
                size = path.stat().st_size
            else:
                # Serialize and optionally compress other data
                path = self._get_cache_path(key)
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

    def get(self, key: str) -> Optional[Any]:
        """Get item from cache with decompression support.
        
        Args:
            key: Cache key
            
        Returns:
            Cached item or None if not found
        """
        # Try different extensions in order of likelihood
        extensions = ['.pkl', '.mp4', '.mp3', '.wav']
        
        for ext in extensions:
            path = self._get_cache_path(key, ext)
            if path.exists():
                try:
                    # Return path for media files
                    if ext in ['.mp4', '.mp3', '.wav']:
                        self._update_stats(hit=True)
                        return str(path)
                    
                    # Deserialize other data
                    data = path.read_bytes()
                    try:
                        data = zlib.decompress(data)
                    except zlib.error:
                        pass
                    
                    data = pickle.loads(data)
                    self._update_stats(hit=True)
                    return data
                    
                except Exception as e:
                    log.warning(f"Failed to read cache item {key}: {e}")
                    continue
        
        self._update_stats(hit=False)
        return None

    def _should_cleanup(self) -> bool:
        """Check if cleanup is needed."""
        total_size = sum(
            f.stat().st_size
            for f in self.base_dir.rglob("*")
            if f.is_file()
        )
        return total_size > self.max_size * self.cleanup_threshold

    def cleanup(self) -> None:
        """Clean up old cache files."""
        try:
            files = []
            for path in self.base_dir.rglob("*"):
                if path.is_file():
                    files.append((path, path.stat().st_mtime))
                    
            files.sort(key=lambda x: x[1])
            total_size = sum(path.stat().st_size for path, _ in files)
            
            for path, _ in files:
                if total_size <= self.max_size * 0.8:
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
        """Calculate cache hit rate."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0

# Initialize global cache instance
cache = CacheManager() 