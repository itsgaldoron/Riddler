"""OpenAI service implementation."""

import os
import json
import hashlib
import time
from typing import Dict, Optional, Any, List
from openai import OpenAI
from riddler.config.exceptions import OpenAIError
from riddler.services.openai.base import OpenAIServiceBase
from riddler.utils.cache import CacheManager
from riddler.utils.logger import log
from pydantic import BaseModel, Field
from pathlib import Path

class RiddleItem(BaseModel):
    riddle: str = Field(description="The riddle text")
    answer: str = Field(description="The answer to the riddle")

class RiddleResponse(BaseModel):
    riddles: List[RiddleItem] = Field(description="List of riddles and their answers")

class SimilarityResponse(BaseModel):
    similarities: List[bool] = Field(description="List of boolean values indicating if each riddle is too similar")

class OpenAIService(OpenAIServiceBase):
    """OpenAI service implementation."""
    
    def __init__(
        self,
        config: Dict,
        api_key: Optional[str] = None,
        logger=None
    ):
        """Initialize OpenAI service."""
        self.config = config
        self.logger = logger or log
        
        # Get API key
        self.api_key = api_key or os.getenv("RIDDLER_OPENAI_API_KEY")
        if not self.api_key:
            raise OpenAIError("OpenAI API key not found")
        
        # Initialize OpenAI client
        self.client = OpenAI(api_key=self.api_key)
        
        # Get model configuration
        self.model = config.get("openai", {}).get("model", "gpt-4o-mini-2024-07-18")
        self.temperature = config.get("openai", {}).get("temperature", 0.7)
        self.max_tokens = config.get("openai", {}).get("max_tokens", 500)
        self.max_attempts = config.get("openai", {}).get("max_attempts", 3)
        
        # Initialize cache
        cache_dir = config.get("openai", {}).get("cache_dir", "cache/riddles")
        self.cache = CacheManager(cache_dir, config=config)
        self._cache_dir = Path(cache_dir)
        
        # Load templates and difficulty levels
        self.templates = config.get("openai", {}).get("riddle_generation", {}).get("templates", {})
        self.difficulty_levels = config.get("openai", {}).get("riddle_generation", {}).get("difficulty_levels", {})

    def _generate_similarity_check(self, prompt: str) -> List[bool]:
        """Generate a similarity check using the OpenAI API."""
        try:
            completion = self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": "Check if any new riddles are too similar to existing ones."}
                ],
                temperature=0.3,
                max_tokens=self.max_tokens,
                response_format=SimilarityResponse
            )
            
            return completion.choices[0].message.parsed.similarities
            
        except Exception as e:
            raise OpenAIError(f"Failed to check similarities: {str(e)}")

    def _batch_similarity_check(self, new_riddles: List[Dict[str, str]], existing_riddles: List[Dict[str, str]], threshold: float = 0.8) -> List[bool]:
        """Batch check similarity of multiple riddles."""
        if not existing_riddles:
            return [False] * len(new_riddles)

        # First do quick exact match checks
        too_similar = []
        remaining_riddles = []
        for riddle in new_riddles:
            riddle_text = riddle["riddle"].lower().strip()
            riddle_answer = riddle["answer"].lower().strip()
            
            is_similar = False
            for existing in existing_riddles:
                existing_text = existing["riddle"].lower().strip()
                existing_answer = existing["answer"].lower().strip()
                
                if riddle_text == existing_text or riddle_answer == existing_answer:
                    is_similar = True
                    break
            
            too_similar.append(is_similar)
            if not is_similar:
                remaining_riddles.append(riddle)

        if not remaining_riddles:
            return too_similar

        # For remaining riddles, do one batch similarity check
        prompt = f"""Analyze the following riddles and determine if any new riddles are too similar to existing ones.
A riddle is considered too similar if it:
1. Uses the same core concept or theme
2. Has a very similar solution approach
3. Uses similar word patterns or structure
4. Has similarity score >= {threshold}

Existing riddles:
"""
        for i, riddle in enumerate(existing_riddles[:40], 1):  # Limit to 10 most recent for comparison
            prompt += f"{i}. Q: {riddle['riddle']}\n   A: {riddle['answer']}\n"
        
        prompt += "\nNew riddles to check:\n"
        for i, riddle in enumerate(remaining_riddles, 1):
            prompt += f"{i}. Q: {riddle['riddle']}\n   A: {riddle['answer']}\n"

        try:
            similarity_results = self._generate_similarity_check(prompt)
            if isinstance(similarity_results, list) and len(similarity_results) == len(remaining_riddles):
                # Merge results back into the original list
                result_idx = 0
                for i in range(len(too_similar)):
                    if not too_similar[i]:
                        too_similar[i] = similarity_results[result_idx]
                        result_idx += 1
        except Exception as e:
            self.logger.warning(f"Failed to batch check similarity: {e}")
            # If batch check fails, assume remaining riddles are not similar
            pass

        return too_similar

    def _prepare_riddle_prompt(
        self,
        category: str,
        num_riddles: int,
        difficulty: str,
        style: str,
        target_age: str,
        educational: bool
    ) -> str:
        """Prepare riddle generation prompt with examples of recent riddles."""
        # Get category-specific configuration
        category_config = self.templates.get(category, {})
        system_prompt = category_config.get("system_prompt", "You are an expert at creating engaging riddles.")
        example_format = category_config.get("example_format", "")
        
        # Get difficulty configuration
        difficulty_config = self.difficulty_levels.get(difficulty, {})
        educational_level = difficulty_config.get("educational_level", "general")
        
        # Get recent riddles for this category (limit to 5 most recent)
        recent_riddles = self._get_category_riddles(category, limit=40)  # Reduced from 20 to 5
        existing_riddles_prompt = ""
        if recent_riddles:
            existing_riddles_prompt = "\n\nRecent riddles (DO NOT create similar riddles):\n"
            for i, riddle in enumerate(recent_riddles, 1):
                existing_riddles_prompt += f"{i}. Q: {riddle['riddle']}\n   A: {riddle['answer']}\n"

        return f"""Create {num_riddles} unique {difficulty} difficulty riddles about {category}.
Each riddle must be COMPLETELY DIFFERENT from any previously asked riddles.
Style: {style}
Target Age: {target_age}
Educational Level: {educational_level}
Make them {"educational and " if educational else ""}engaging.

{system_prompt}

{f"Example format: {example_format}" if example_format else ""}

STRICT REQUIREMENTS:
1. Each riddle must be completely unique in concept, structure, and solution
2. Do not reuse any themes, concepts, or answers from the recent riddles
3. Avoid similar word patterns or phrasings
4. Each riddle should focus on a different aspect of {category}
5. If a concept was used in a recent riddle, choose a completely different one{existing_riddles_prompt}

Response must be a list of {num_riddles} objects, each containing 'riddle' and 'answer' fields."""

    def generate_riddle(
        self,
        category: str,
        num_riddles: int = 1,
        difficulty: str = "medium",
        style: str = "classic",
        target_age: str = "teen",
        educational: bool = True,
        cache_key: Optional[str] = None,
        no_cache: bool = False
    ) -> List[Dict[str, str]]:
        """Generate multiple unique riddles using OpenAI.
        
        Args:
            category: Riddle category
            num_riddles: Number of unique riddles to generate
            difficulty: Difficulty level
            style: Riddle style
            target_age: Target age group
            educational: Whether to include educational content
            cache_key: Optional cache key
            no_cache: Whether to skip cache checking
            
        Returns:
            List of dictionaries containing riddles and answers
            
        Raises:
            OpenAIError: If generation fails
        """
        try:
            # Validate inputs
            self._validate_category(category)
            self._validate_difficulty(difficulty)
            
            # Create category directory if it doesn't exist
            category_dir = self._cache_dir / category
            category_dir.mkdir(parents=True, exist_ok=True)
            
            # Get existing riddles for similarity check
            existing_riddles = self._get_category_riddles(category) if not no_cache else []
            
            # Generate cache key if not provided and caching is enabled
            if not no_cache:
                if not cache_key:
                    # Include category in cache key generation
                    timestamp = int(time.time())
                    params = {
                        "category": category,
                        "num_riddles": num_riddles,
                        "difficulty": difficulty,
                        "style": style,
                        "target_age": target_age,
                        "educational": educational,
                        "timestamp": timestamp
                    }
                    cache_key = f"{category}/{hashlib.sha256(json.dumps(params, sort_keys=True).encode()).hexdigest()}"
                
                if cache_key:
                    self.logger.info(f"Cache key: {cache_key}")
                    # Check cache
                    cached_data = self.cache.get(cache_key)
                    if cached_data and isinstance(cached_data, list):
                        self.logger.info("Using cached riddles")
                        return cached_data
            else:
                self.logger.info("Cache disabled, generating new riddles")
            
            # Prepare prompt with recent riddles
            prompt = self._prepare_riddle_prompt(
                category,
                num_riddles,
                difficulty,
                style,
                target_age,
                educational
            )
            # Generate riddles
            for attempt in range(self.max_attempts):
                try:
                    response = self._generate_completion(
                        prompt,
                        temperature=self.temperature + (attempt * 0.1)
                    )
                    
                    # Parse response
                    riddle_data = self._parse_riddle_response(response)
                    
                    # Basic validation
                    if not all(self._validate_riddle(r) for r in riddle_data):
                        continue
                    
                    # Batch similarity check
                    if existing_riddles:
                        too_similar = self._batch_similarity_check(riddle_data, existing_riddles)
                        self.logger.info(f"Similarity check results: {too_similar}")
                        if any(too_similar):
                            continue
                    
                    break
                        
                except Exception as e:
                    if attempt == self.max_attempts - 1:
                        raise OpenAIError(f"Failed to generate valid riddles: {str(e)}")
                    self.logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                    continue
            
            # Add metadata to each riddle
            for riddle in riddle_data:
                riddle.update({
                    "category": category,
                    "difficulty": difficulty,
                    "style": style,
                    "target_age": target_age,
                    "timestamp": int(time.time())
                })
            
            # Cache result if we have a valid key
            if cache_key and not no_cache:
                # Save in category directory
                cache_file = category_dir / f"{hashlib.sha256(json.dumps(riddle_data[0]['riddle'], sort_keys=True).encode()).hexdigest()}.json"
                try:
                    with open(cache_file, 'w') as f:
                        json.dump(riddle_data, f, indent=2)
                    self.logger.info(f"Saved riddles to {cache_file}")
                except Exception as e:
                    self.logger.warning(f"Failed to save riddles to file: {e}")
                
                # Also save in main cache for backward compatibility
                self.cache.put(cache_key, riddle_data)
            
            return riddle_data
            
        except Exception as e:
            self.logger.error(f"Failed to generate riddles: {str(e)}")
            raise OpenAIError(f"Failed to generate riddles: {str(e)}")

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
                    {"role": "user", "content": "Generate unique riddles based on the given category and requirements."}
                ],
                temperature=temperature or self.temperature,
                max_tokens=self.max_tokens,
                response_format=RiddleResponse
            )
            
            return [
                {"riddle": item.riddle, "answer": item.answer}
                for item in completion.choices[0].message.parsed.riddles
            ]
            
        except Exception as e:
            raise OpenAIError(f"Failed to generate completion: {str(e)}")

    def _parse_riddle_response(self, data: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Parse and validate the riddle response.
        
        Args:
            data: Response data to parse
            
        Returns:
            Validated riddle data
            
        Raises:
            OpenAIError: If validation fails
        """
        try:
            if not isinstance(data, list):
                raise OpenAIError("Response is not a list")
                
            parsed_riddles = []
            for riddle_data in data:
                if not isinstance(riddle_data, dict):
                    raise OpenAIError("Riddle data is not a dictionary")
                    
                required_fields = ["riddle", "answer"]
                for field in required_fields:
                    if field not in riddle_data:
                        raise OpenAIError(f"Missing required field '{field}'")
                    if not isinstance(riddle_data[field], str):
                        raise OpenAIError(f"Field '{field}' must be a string")
                    if not riddle_data[field].strip():
                        raise OpenAIError(f"Field '{field}' cannot be empty")
                
                parsed_riddles.append({
                    "riddle": riddle_data["riddle"].strip(),
                    "answer": riddle_data["answer"].strip(),
                })
            
            return parsed_riddles
            
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

    def _get_category_riddles(self, category: str, limit: Optional[int] = None) -> List[Dict[str, str]]:
        """Get cached riddles for a category.
        
        Args:
            category: The riddle category
            limit: Optional limit of most recent riddles to return
            
        Returns:
            List of cached riddles for the category
        """
        try:
            # Get all cache files in the category subdirectory
            category_dir = self._cache_dir / category
            if not category_dir.exists():
                return []
                
            riddles = []
            for cache_file in category_dir.glob("*.json"):
                try:
                    with open(cache_file) as f:
                        data = json.load(f)
                    if isinstance(data, list):
                        riddles.extend(data)
                except Exception as e:
                    self.logger.warning(f"Failed to read cache file {cache_file}: {e}")
            
            # Sort by timestamp if available and return most recent
            riddles.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
            if limit and len(riddles) > limit:
                riddles = riddles[:limit]
                    
            return riddles
        except Exception as e:
            self.logger.warning(f"Failed to get cached riddles for category {category}: {e}")
            return []

    def validate_response(self, response: Dict) -> bool:
        """Validate OpenAI response format.
        
        Args:
            response: Response from OpenAI
            
        Returns:
            True if valid, False otherwise
        """
        return self._validate_riddle(response) 