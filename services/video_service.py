"""Video service using Pexels API"""

import json
import os
import random
import requests
from typing import Optional
import hashlib

from utils.cache import CacheManager
from utils.helpers import get_api_key
from utils.logger import log, StructuredLogger
from utils.validators import validate_category
from config.exceptions import VideoError

class VideoService:
    """Service for retrieving videos from Pexels"""
    
    def __init__(
        self,
        min_duration: int = 3,
        max_duration: int = 3,
        min_width: int = 1080,
        min_height: int = 1920,
        orientation: str = "portrait",
        cache_dir: str = "cache/video",
        logger: Optional[StructuredLogger] = None
    ):
        """Initialize video service
        
        Args:
            min_duration: Minimum video duration in seconds
            max_duration: Maximum video duration in seconds
            min_width: Minimum video width
            min_height: Minimum video height
            orientation: Video orientation (portrait/landscape)
            cache_dir: Cache directory for videos
            logger: Logger instance
        """
        self.api_key = get_api_key("pexels")
        self.min_duration = min_duration
        self.max_duration = max_duration
        self.min_width = min_width
        self.min_height = min_height
        self.orientation = orientation
        self.base_url = "https://api.pexels.com/videos"
        self.cache = CacheManager(cache_dir)
        self.logger = logger or log
        
        # Category to search term mapping
        self.category_terms = {
            "geography": [
                "landscape", "mountains", "ocean",
                "desert", "forest", "waterfall"
            ],
            "math": [
                "numbers", "geometry", "patterns",
                "symmetry", "fractals", "shapes"
            ],
            "physics": [
                "motion", "energy", "light",
                "space", "gravity", "waves"
            ],
            "history": [
                "ancient", "ruins", "architecture",
                "monuments", "artifacts", "time"
            ],
            "logic": [
                "puzzle", "maze", "chess",
                "strategy", "problem solving", "thinking"
            ],
            "wordplay": [
                "letters", "books", "writing",
                "library", "words", "communication"
            ]
        }
    
    def get_video(self, category: str) -> str:
        """Get a video for the given category
        
        Args:
            category: Video category
            
        Returns:
            Path to video file
            
        Raises:
            VideoError: If video retrieval fails
        """
        try:
            # Validate category
            validate_category(category)
            
            # Get search terms for category
            search_terms = self.category_terms.get(category.lower())
            if not search_terms:
                raise VideoError(f"No search terms found for category: {category}")
            
            # Try each search term until we find a suitable video
            for term in random.sample(search_terms, len(search_terms)):
                try:
                    # Generate cache key
                    params = {
                        "category": category,
                        "term": term,
                        "orientation": self.orientation,
                        "min_duration": str(self.min_duration),
                        "max_duration": str(self.max_duration)
                    }
                    cache_key = hashlib.sha256(
                        json.dumps(params, sort_keys=True).encode()
                    ).hexdigest()
                    
                    # Check cache
                    cached_file = self.cache.get(cache_key)
                    if cached_file and os.path.exists(cached_file):
                        self.logger.debug(f"Using cached video: {cached_file}")
                        return str(cached_file)
                    
                    # Search for videos
                    url = f"{self.base_url}/search"
                    headers = {"Authorization": self.api_key}
                    params = {
                        "query": term,
                        "orientation": self.orientation,
                        "size": "large",
                        "per_page": 15
                    }
                    
                    # Make request
                    response = requests.get(url, headers=headers, params=params)
                    response.raise_for_status()
                    
                    # Parse response
                    data = response.json()
                    if not data.get("videos"):
                        continue
                    
                    # Filter videos by requirements
                    suitable_videos = []
                    for video in data["videos"]:
                        if not (self.min_duration <= video["duration"] <= self.max_duration):
                            continue
                        
                        # Find suitable video file
                        video_files = sorted(
                            video["video_files"],
                            key=lambda x: (x.get("width", 0) * x.get("height", 0)),
                            reverse=True
                        )
                        
                        for video_file in video_files:
                            if (video_file.get("width", 0) >= self.min_width and
                                video_file.get("height", 0) >= self.min_height):
                                suitable_videos.append((video, video_file))
                                break
                    
                    if not suitable_videos:
                        continue
                    
                    # Select random video
                    video, video_file = random.choice(suitable_videos)
                    
                    # Download video
                    video_url = video_file["link"]
                    response = requests.get(video_url, stream=True)
                    response.raise_for_status()
                    
                    # Save video file
                    output_path = os.path.join(
                        self.cache.cache_dir,
                        f"{cache_key}.mp4"
                    )
                    
                    # Ensure directory exists
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    
                    # Download with progress
                    with open(output_path, "wb") as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                    
                    # Verify the downloaded file
                    if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                        raise VideoError("Downloaded file is empty or does not exist")
                    
                    # Add to cache
                    self.cache.put(cache_key, output_path)
                    self.logger.debug(f"Cached video: {output_path}")
                    
                    return str(output_path)
                    
                except Exception as e:
                    self.logger.error(f"Error getting video for term '{term}': {str(e)}")
                    continue
            
            raise VideoError(f"No suitable videos found for category: {category}")
            
        except Exception as e:
            raise VideoError(f"Failed to get video: {str(e)}") 