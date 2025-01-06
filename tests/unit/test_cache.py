"""Unit tests for cache manager"""

import pytest
from pathlib import Path
from utils.cache import CacheManager

@pytest.fixture
def cache_manager(tmp_path):
    """Create cache manager instance"""
    return CacheManager(str(tmp_path), 1000)

def test_init(tmp_path):
    """Test cache manager initialization"""
    cache_dir = tmp_path / "cache"
    manager = CacheManager(str(cache_dir), 1000)
    assert cache_dir.exists()
    assert cache_dir.is_dir()

def test_get_missing(cache_manager):
    """Test getting missing cache item"""
    result = cache_manager.get("nonexistent")
    assert result is None

def test_put_and_get(cache_manager, tmp_path):
    """Test putting and getting cache item"""
    # Create test file
    source_file = tmp_path / "test.txt"
    source_file.write_text("test content")
    
    # Put in cache
    cached_path = cache_manager.put("test_key", source_file)
    assert cached_path.exists()
    assert cached_path.read_text() == "test content"
    
    # Get from cache
    result = cache_manager.get("test_key")
    assert result == cached_path
    assert result.read_text() == "test content"

def test_cleanup_trigger(cache_manager, tmp_path):
    """Test cache cleanup triggering"""
    # Create test files
    for i in range(5):
        source_file = tmp_path / f"test_{i}.txt"
        source_file.write_text("x" * 300)  # Each file is 300 bytes
        cache_manager.put(f"key_{i}", source_file)
    
    # Cache should be cleaned up (max size is 1000 bytes)
    files = list(Path(cache_manager.cache_dir).glob("*"))
    total_size = sum(f.stat().st_size for f in files)
    assert total_size <= cache_manager.max_size

def test_should_cleanup(cache_manager, tmp_path):
    """Test should_cleanup check"""
    # Create file larger than max size
    source_file = tmp_path / "large.txt"
    source_file.write_text("x" * 2000)  # 2000 bytes
    cache_manager.put("large", source_file)
    
    assert cache_manager.should_cleanup()

def test_cleanup_removes_oldest(cache_manager, tmp_path):
    """Test cleanup removes oldest files first"""
    # Create test files with different timestamps
    files = []
    for i in range(3):
        source_file = tmp_path / f"test_{i}.txt"
        source_file.write_text("x" * 400)  # Each file is 400 bytes
        cached_path = cache_manager.put(f"key_{i}", source_file)
        files.append(cached_path)
    
    # First file should be removed (oldest)
    assert not files[0].exists()
    assert files[1].exists()
    assert files[2].exists() 