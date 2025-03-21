"""OpenAI service implementation."""

import os
import json
import hashlib
from typing import Dict, Optional, Any
from openai import OpenAI
from config.exceptions import OpenAIError
from services.openai.base import OpenAIServiceBase
from utils.cache import CacheManager
from utils.logger import log
from pydantic import BaseModel

class RiddleResponse(BaseModel):
    riddle: str
    answer: str

class OpenAIService(OpenAIServiceBase):
    """OpenAI service implementation."""
    
    def __init__(
        self,
        config: Dict,
        api_key: Optional[str] = None,
        logger=None
    ):
        """Initialize OpenAI service.
        
        Args:
            config: Configuration dictionary
            api_key: OpenAI API key (defaults to env var)
            logger: Optional logger instance
        """
        self.config = config
        self.logger = logger or log
        
        # Get API key
        self.api_key = api_key or os.getenv("RIDDLER_OPENAI_API_KEY")
        if not self.api_key:
            raise OpenAIError("OpenAI API key not found")
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.api_key)
        
        # Get model configuration
        self.model = config.get("openai", {}).get("model", "gpt-4o-2024-08-06")
        self.temperature = config.get("openai", {}).get("temperature", 0.7)
        self.max_tokens = config.get("openai", {}).get("max_tokens", 500)
        self.max_attempts = config.get("openai", {}).get("max_attempts", 3)
        
        # Initialize cache
        cache_dir = config.get("openai", {}).get("cache_dir", "cache/riddles")
        self.cache = CacheManager(cache_dir)
        
        # Load templates and difficulty levels
        self.templates = config.get("openai", {}).get("riddle_generation", {}).get("templates", {})
        self.difficulty_levels = config.get("openai", {}).get("riddle_generation", {}).get("difficulty_levels", {})

    def generate_riddle(
        self,
        category: str,
        difficulty: str = "medium",
        style: str = "classic",
        target_age: str = "teen",
        educational: bool = True,
        cache_key: Optional[str] = None,
        no_cache: bool = False
    ) -> Dict[str, str]:
        """Generate a riddle using OpenAI.
        
        Args:
            category: Riddle category
            difficulty: Difficulty level
            style: Riddle style
            target_age: Target age group
            educational: Whether to include educational content
            cache_key: Optional cache key
            no_cache: Whether to skip cache checking
            
        Returns:
            Dictionary containing riddle and answer
            
        Raises:
            OpenAIError: If generation fails
        """
        try:
            # Validate inputs
            self._validate_category(category)
            self._validate_difficulty(difficulty)
            
            # Generate cache key if not provided and caching is enabled
            if not no_cache:
                if not cache_key:
                    params = {
                        "category": category,
                        "difficulty": difficulty,
                        "style": style,
                        "target_age": target_age,
                        "educational": educational
                    }
                    cache_key = hashlib.sha256(
                        json.dumps(params, sort_keys=True).encode()
                    ).hexdigest()
                
                self.logger.info(f"Cache key: {cache_key}")
                # Check cache
                cached_data = self.cache.get(cache_key)
                if cached_data and isinstance(cached_data, dict):
                    self.logger.info("Using cached riddle")
                    return cached_data
            else:
                self.logger.info("Cache disabled, generating new riddle")
                # Generate a cache key anyway for potential storage
                params = {
                    "category": category,
                    "difficulty": difficulty,
                    "style": style,
                    "target_age": target_age,
                    "educational": educational
                }
                cache_key = hashlib.sha256(
                    json.dumps(params, sort_keys=True).encode()
                ).hexdigest()
            
            # Prepare prompt
            prompt = self._prepare_riddle_prompt(
                category,
                difficulty,
                style,
                target_age,
                educational
            )
            
            # Generate riddle
            for attempt in range(self.max_attempts):
                try:
                    response = self._generate_completion(
                        prompt,
                        temperature=self.temperature + (attempt * 0.1)
                    )
                    
                    # Parse and validate response
                    riddle_data = self._parse_riddle_response(response)
                    if self._validate_riddle(riddle_data):
                        break
                        
                except Exception as e:
                    if attempt == self.max_attempts - 1:
                        raise OpenAIError(f"Failed to generate valid riddle: {str(e)}")
                    self.logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                    continue
            
            # Add metadata
            riddle_data.update({
                "category": category,
                "difficulty": difficulty,
                "style": style,
                "target_age": target_age
            })
            
            # Cache result if caching is enabled
            if not no_cache and cache_key:
                self.cache.put(cache_key, riddle_data)
            
            return riddle_data
            
        except Exception as e:
            self.logger.error(f"Failed to generate riddle: {str(e)}")
            raise OpenAIError(f"Failed to generate riddle: {str(e)}")

    def _generate_completion(self, prompt: str, temperature: Optional[float] = None) -> Dict[str, Any]:
        """Generate a completion using the OpenAI API.
        
        Args:
            prompt: The prompt to generate from
            temperature: Optional temperature override
            
        Returns:
            The generated completion data
            
        Raises:
            OpenAIError: If generation fails
        """
        try:
            completion = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": "Generate a riddle based on the given category and requirements."}
                ],
                temperature=temperature or self.temperature,
                max_tokens=self.max_tokens,
                response_format=RiddleResponse
            )
            
            return {
                "riddle": completion.choices[0].message.parsed.riddle,
                "answer": completion.choices[0].message.parsed.answer,
            }
            
        except Exception as e:
            raise OpenAIError(f"Failed to generate completion: {str(e)}")

    def _parse_riddle_response(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Parse and validate the riddle response.
        
        Args:
            data: Response data to parse
            
        Returns:
            Validated riddle data
            
        Raises:
            OpenAIError: If validation fails
        """
        try:
            if not isinstance(data, dict):
                raise OpenAIError("Response is not a dictionary")
                
            required_fields = ["riddle", "answer"]
            for field in required_fields:
                if field not in data:
                    raise OpenAIError(f"Missing required field '{field}'")
                if not isinstance(data[field], str):
                    raise OpenAIError(f"Field '{field}' must be a string")
                if not data[field].strip():
                    raise OpenAIError(f"Field '{field}' cannot be empty")
            
            return {
                "riddle": data["riddle"].strip(),
                "answer": data["answer"].strip(),
            }
            
        except Exception as e:
            raise OpenAIError(f"Invalid riddle data format: {str(e)}")

    def _validate_riddle(self, riddle_data: Dict[str, str]) -> bool:
        """Validate riddle data.
        
        Args:
            riddle_data: Dictionary with riddle and answer
            
        Returns:
            Whether the riddle is valid
        """
        try:
            required_fields = ["riddle", "answer"]
            
            # Check required fields
            for field in required_fields:
                if field not in riddle_data:
                    self.logger.info(f"Missing field: {field}")
                    return False
                if not isinstance(riddle_data[field], str):
                    self.logger.info(f"Field {field} is not a string")
                    return False
                if not riddle_data[field].strip():
                    self.logger.info(f"Field {field} is empty")
                    return False
            
            # Check field lengths
            if len(riddle_data["riddle"]) < 10:
                self.logger.info("Riddle text too short")
                return False
            if len(riddle_data["answer"]) < 1:
                self.logger.info("Answer text too short")
                return False

            
            # Check for inappropriate content
            if self._contains_inappropriate_content(riddle_data):
                self.logger.info("Contains inappropriate content")
                return False
            
            return True
            
        except Exception as e:
            self.logger.info(f"Validation error: {str(e)}")
            return False

    def _contains_inappropriate_content(self, riddle_data: Dict[str, str]) -> bool:
        """Check for inappropriate content in riddle data.
        
        Args:
            riddle_data: Dictionary with riddle and answer
            
        Returns:
            Whether the content is inappropriate
        """
        # Add content filtering logic here
        return False

    def _validate_category(self, category: str) -> None:
        """Validate riddle category.
        
        Args:
            category: Category to validate
            
        Raises:
            ValueError: If category is invalid
        """
        video_config = self.config.get("video", {})
        pexels_config = video_config.get("pexels", {})
        category_terms = pexels_config.get("category_terms", {})
        valid_categories = list(category_terms.keys())
        self.logger.info(f"Valid categories: {valid_categories}")
        if category not in valid_categories:
            raise ValueError(f"Invalid category: {category}. Must be one of {valid_categories}")

    def _validate_difficulty(self, difficulty: str) -> None:
        """Validate difficulty level.
        
        Args:
            difficulty: Difficulty to validate
            
        Raises:
            ValueError: If difficulty is invalid
        """
        valid_difficulties = ["easy", "medium", "hard"]
        if difficulty not in valid_difficulties:
            raise ValueError(f"Invalid difficulty: {difficulty}. Must be one of {valid_difficulties}")

    def _prepare_riddle_prompt(
        self,
        category: str,
        difficulty: str,
        style: str,
        target_age: str,
        educational: bool
    ) -> str:
        """Prepare riddle generation prompt.
        
        Args:
            category: Riddle category
            difficulty: Difficulty level
            style: Riddle style
            target_age: Target age group
            educational: Whether to include educational content
            
        Returns:
            Formatted prompt
        """
        # Get category-specific configuration
        category_config = self.templates.get(category, {})
        system_prompt = category_config.get("system_prompt", "You are an expert at creating engaging riddles.")
        example_format = category_config.get("example_format", "")
        
        # Get difficulty configuration
        difficulty_config = self.difficulty_levels.get(difficulty, {})
        educational_level = difficulty_config.get("educational_level", "general")
        
        return f"""Create a {difficulty} difficulty riddle about {category}.
Style: {style}`
Target Age: {target_age}
Educational Level: {educational_level}
Make it {"educational and " if educational else ""}engaging.

{system_prompt}

{f"Example format: {example_format}" if example_format else ""}""" 

    def validate_response(self, response: Dict) -> bool:
        """Validate OpenAI response format.
        
        Args:
            response: Response from OpenAI
            
        Returns:
            True if valid, False otherwise
        """
        return self._validate_riddle(response) 