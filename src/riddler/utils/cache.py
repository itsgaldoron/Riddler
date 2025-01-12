"""Cache management utilities"""

import hashlib
import pickle
import zlib
from pathlib import Path
from typing import Any, Optional, Dict
from concurrent.futures import ThreadPoolExecutor
from riddler.utils.logger import log

class CacheConfig:
    """Cache configuration."""
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize cache configuration.
        
        Args:
            config: Configuration dictionary
        """
        config = config or {}
        cache_config = config.get("cache", {})
        
        # Size limits
        self.max_size = cache_config.get("max_cache_size", 10 * 1024 * 1024 * 1024)  # Default 10GB
        self.cleanup_threshold = cache_config.get("cleanup_threshold", 0.9)
        
        # Threading
        self.max_workers = cache_config.get("max_workers", 4)
        
        # Compression
        self.default_compression = cache_config.get("default_compression", 6)
        self.compress_threshold = cache_config.get("compress_threshold", 1024)  # 1KB

class CacheManager:
    """Cache management class."""
    
    def __init__(self, cache_dir: str, config: Optional[Dict] = None):
        """Initialize cache manager.
        
        Args:
            cache_dir: Directory to store cache files
            config: Optional configuration dictionary
        """
        self._cache_dir = Path(cache_dir)
        self._config = CacheConfig(config)
        self.logger = log
        
        # Create cache directory if it doesn't exist
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize executor for async operations
        self.executor = ThreadPoolExecutor(
            max_workers=self._config.max_workers,
            thread_name_prefix="cache"
        )
        
        # Initialize stats
        self.stats = CacheStats()
        self._total_size = self._calculate_total_size()
        
    def _calculate_total_size(self) -> int:
        """Calculate total size of cache directory."""
        return sum(
            f.stat().st_size
            for f in self._cache_dir.rglob("*")
            if f.is_file()
        )

    @property
    def cache_dir(self) -> str:
        """Get the cache directory path."""
        return str(self._cache_dir)

    def _update_stats(self, hit: bool = False, size_delta: int = 0) -> None:
        """Update cache statistics."""
        if hit:
            self.stats.hits += 1
        else:
            self.stats.misses += 1
        
        self._total_size += size_delta
        self.stats.size_bytes = self._total_size
        
        # Save stats
        stats_path = self._cache_dir / "stats.pkl"
        try:
            with open(stats_path, "wb") as f:
                pickle.dump(self.stats, f)
        except Exception as e:
            self.logger.warning(f"Failed to save cache stats: {e}")

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
        path = self._cache_dir / subdir
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
                
                # Apply compression if:
                # 1. Explicitly requested via compression_level
                # 2. Data size exceeds threshold and compression not disabled
                if len(serialized_data) > self._config.compress_threshold:
                    level = compression_level if compression_level is not None else self._config.default_compression
                    if level > 0:
                        serialized_data = zlib.compress(serialized_data, level=level)
                
                path.write_bytes(serialized_data)
                size = path.stat().st_size
                
            self._update_stats(size_delta=size)
            self.stats.items_count += 1
            return True
            
        except Exception as e:
            self.logger.warning(f"Failed to write cache item {key}: {e}")
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
                    self.logger.warning(f"Failed to read cache item {key}: {e}")
                    continue
        
        self._update_stats(hit=False)
        return None

    def _should_cleanup(self) -> bool:
        """Check if cleanup is needed."""
        return self._total_size > self._config.max_size * self._config.cleanup_threshold

    def cleanup(self) -> None:
        """Clean up old cache files."""
        try:
            # Verify total size
            actual_size = self._calculate_total_size()
            if actual_size != self._total_size:
                self._total_size = actual_size  # Correct if drift occurred
            
            files = []
            for path in self._cache_dir.rglob("*"):
                if path.is_file():
                    files.append((path, path.stat().st_mtime))
                    
            files.sort(key=lambda x: x[1])
            total_size = sum(path.stat().st_size for path, _ in files)
            
            for path, _ in files:
                if total_size <= self._config.max_size * 0.8:
                    break
                    
                try:
                    size = path.stat().st_size
                    path.unlink()
                    total_size -= size
                except Exception as e:
                    self.logger.warning(f"Failed to remove cache file {path}: {e}")
                    
        except Exception as e:
            self.logger.error(f"Failed to clean cache: {e}")

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