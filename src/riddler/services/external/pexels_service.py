"""Video service using Pexels API"""

import json
import os
import random
import requests
from typing import Optional, Dict
import hashlib

from riddler.utils.cache import CacheManager
from riddler.utils.helpers import get_api_key
from riddler.utils.logger import log, StructuredLogger
from riddler.utils.validators import validate_category
from riddler.config.exceptions import VideoError

class PexelsService:
    """Service for retrieving videos from Pexels"""
    
    def __init__(
        self,
        config: Dict,
        min_duration: Optional[int] = None,
        max_duration: Optional[int] = None,
        min_width: Optional[int] = None,
        min_height: Optional[int] = None,
        orientation: Optional[str] = None,
        cache_dir: Optional[str] = None,
        logger: Optional[StructuredLogger] = None
    ):
        """Initialize video service
        
        Args:
            config: Configuration dictionary
            min_duration: Minimum video duration in seconds
            max_duration: Maximum video duration in seconds
            min_width: Minimum video width
            min_height: Minimum video height
            orientation: Video orientation (portrait/landscape)
            cache_dir: Cache directory for videos
            logger: Logger instance
        """
        self.api_key = get_api_key("pexels")
        self.min_duration = min_duration or config.get("video", {}).get("pexels", {}).get("min_duration", 3)
        self.max_duration = max_duration or config.get("video", {}).get("pexels", {}).get("max_duration", 3)
        self.min_width = min_width or config.get("video", {}).get("pexels", {}).get("min_width", 1080)
        self.min_height = min_height or config.get("video", {}).get("pexels", {}).get("min_height", 1920)
        self.orientation = orientation or config.get("video", {}).get("pexels", {}).get("orientation", "portrait")
        self.base_url = "https://api.pexels.com/videos"
        self.cache = CacheManager(cache_dir or config.get("video", {}).get("pexels", {}).get("cache_dir", "cache/video"))
        self.logger = logger or log
        
        # Get category terms from config - fix nested access
        pexels_config = config.get("video", {}).get("pexels", {})
        self.category_terms = pexels_config.get("category_terms", {})
        self.logger.info(f"Loaded category terms: {list(self.category_terms.keys())}")
    
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
                        self.logger.info(f"Using cached video: {cached_file}")
                        return str(cached_file)
                    
                    # Search for videos
                    url = f"{self.base_url}/search"
                    headers = {
                        "Authorization": f"{self.api_key}"
                    }
                    params = {
                        "query": term,
                        "orientation": self.orientation,
                        "size": "large",
                        "per_page": 15,
                        "min_duration": self.min_duration,
                        "max_duration": self.max_duration,
                        "min_width": self.min_width,
                        "min_height": self.min_height
                    }
                    
                    # Make request
                    self.logger.info(f"Searching Pexels for term: {term}")
                    self.logger.info(f"Request params: {params}")
                    self.logger.info(f"Using API key: {self.api_key[:10]}...")
                    response = requests.get(url, headers=headers, params=params)
                    
                    if response.status_code != 200:
                        self.logger.error(f"Pexels API error: {response.status_code} - {response.text}")
                        continue
                        
                    response.raise_for_status()
                    
                    # Parse response
                    data = response.json()
                    self.logger.info(f"Found {len(data.get('videos', []))} videos")
                    if not data.get("videos"):
                        continue
                    
                    # Filter videos by requirements
                    suitable_videos = []
                    for video in data["videos"]:
                        # Find suitable video file
                        video_files = sorted(
                            video["video_files"],
                            key=lambda x: (x.get("width", 0) * x.get("height", 0)),
                            reverse=True
                        )
                        
                        for video_file in video_files:
                            width = video_file.get("width", 0)
                            height = video_file.get("height", 0)
                            
                            # Check if dimensions are acceptable
                            if width >= 720 and height >= 1280:  # Reduced requirements
                                suitable_videos.append((video, video_file))
                                self.logger.info(
                                    f"Found suitable video: {width}x{height}, "
                                    f"duration: {video.get('duration')}s"
                                )
                                break
                    
                    if not suitable_videos:
                        self.logger.info("No suitable videos found with current criteria")
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
                    self.logger.info(f"Cached video: {output_path}")
                    
                    return str(output_path)
                    
                except Exception as e:
                    self.logger.error(f"Error getting video for term '{term}': {str(e)}")
                    continue
            
            raise VideoError(f"No suitable videos found for category: {category}")
            
        except Exception as e:
            raise VideoError(f"Failed to get video: {str(e)}") 