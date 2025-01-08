"""OpenAI service for riddle generation and content creation"""

import os
from typing import Dict, Any, List, Optional
from openai import OpenAI, OpenAIError as OAIError
from utils.logger import log, StructuredLogger
from utils.cache import CacheManager
from utils.validators import validate_category, validate_difficulty
from config.exceptions import OpenAIError
from config.config import Config
import json
import hashlib

def validate_category(category: str) -> None:
    """Validate riddle category.
    
    Args:
        category: Category to validate
        
    Raises:
        ValueError: If category is invalid
    """
    valid_categories = [
        "geography",
        "math",
        "physics",
        "history",
        "logic",
        "wordplay"
    ]
    if category not in valid_categories:
        raise ValueError(f"Invalid category: {category}. Must be one of {valid_categories}")

def validate_difficulty(difficulty: str) -> None:
    """Validate difficulty level.
    
    Args:
        difficulty: Difficulty to validate
        
    Raises:
        ValueError: If difficulty is invalid
    """
    valid_difficulties = ["easy", "medium", "hard"]
    if difficulty not in valid_difficulties:
        raise ValueError(f"Invalid difficulty: {difficulty}. Must be one of {valid_difficulties}")

class OpenAIService:
    """Service for generating riddles and educational content using OpenAI."""
    
    def __init__(
        self,
        config: Config,
        api_key: Optional[str] = None,
        logger: Optional[StructuredLogger] = None,
    ):
        """Initialize OpenAI service.
        
        Args:
            config: Config instance
            api_key: OpenAI API key (defaults to env var)
            logger: Logger instance
        """
        self.config = config
        self.api_key = api_key or os.getenv("RIDDLER_OPENAI_API_KEY")
        if not self.api_key:
            raise OpenAIError("OpenAI API key not found")
            
        self.client = OpenAI(api_key=self.api_key)
        self.model = self.config.get("openai.model", "gpt-4o-2024-08-06")
        self.temperature = self.config.get("openai.temperature", 0.7)
        self.max_tokens = self.config.get("openai.max_tokens", 500)
        self.max_attempts = self.config.get("openai.max_attempts", 3)
        self.logger = logger or log
        
        cache_dir = self.config.get("openai.cache_dir", "cache/riddles")
        self.cache = CacheManager(cache_dir)
        
        # Load templates and difficulty levels from config
        self.templates = self.config.get("openai.riddle_generation.templates", {})
        self.difficulty_levels = self.config.get("openai.riddle_generation.difficulty_levels", {})
        
    def generate_riddle(
        self,
        category: str,
        difficulty: str = "medium",
        style: str = "classic",
        target_age: str = "teen",
        educational: bool = True,
        cache_key: Optional[str] = None
    ) -> Dict[str, str]:
        """Generate a riddle using OpenAI.
        
        Args:
            category: Riddle category
            difficulty: Difficulty level
            style: Riddle style
            target_age: Target age group
            educational: Whether to include educational content
            cache_key: Optional cache key
            
        Returns:
            Dictionary with riddle and answer
            
        Raises:
            OpenAIError: If generation fails
        """
        try:
            # Validate inputs
            validate_category(category)
            validate_difficulty(difficulty)
            
            # Generate cache key if not provided
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
            
            # Check cache
            cached_data = self.cache.get(cache_key)
            if cached_data and isinstance(cached_data, dict):
                self.logger.cache_operation("get", cache_key, True)
                return cached_data
            
            # Prepare prompt
            prompt = self._prepare_riddle_prompt(
                category,
                difficulty,
                style,
                target_age,
                educational
            )
            self.logger.debug(f"Generated prompt: {prompt}")
            
            # Generate riddle
            for attempt in range(self.max_attempts):
                try:
                    self.logger.debug(f"Attempt {attempt + 1} to generate riddle")
                    response = self._generate_completion(
                        prompt,
                        temperature=self.temperature + (attempt * 0.1)
                    )
                    
                    # Parse response
                    self.logger.debug(f"Raw response from OpenAI: {response}")
                    riddle_data = self._parse_riddle_response(response)
                    self.logger.debug(f"Parsed riddle data: {riddle_data}")
                    
                    if self._validate_riddle(riddle_data):
                        self.logger.debug("Riddle validation successful")
                        break
                    else:
                        self.logger.debug("Riddle validation failed")
                except Exception as e:
                    self.logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                    self.logger.error(f"Exception type: {type(e)}")
                    import traceback
                    self.logger.error(f"Traceback: {traceback.format_exc()}")
                    if attempt == self.max_attempts - 1:
                        raise OpenAIError(f"Failed to generate valid riddle: {str(e)}")
                    continue
            
            # Add metadata
            riddle_data.update({
                "category": category,
                "difficulty": difficulty,
                "style": style,
                "target_age": target_age
            })
            
            # Cache result
            self.cache.put(cache_key, riddle_data)
            self.logger.cache_operation("put", cache_key, True)
            
            return riddle_data
            
        except Exception as e:
            self.logger.error(f"Failed to generate riddle: {str(e)}")
            self.logger.error(f"Exception type: {type(e)}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            raise OpenAIError(f"Failed to generate riddle: {str(e)}")
    
    def _generate_completion(self, prompt: str, temperature: Optional[float] = None) -> Dict[str, str]:
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
            response = self.client.chat.completions.create(
                model="gpt-4o-2024-08-06",
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": "Generate a riddle based on the given category and requirements."}
                ],
                temperature=temperature or self.temperature,
                max_tokens=self.max_tokens,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "riddle",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "riddle": {
                                    "type": "string",
                                    "description": "The riddle text"
                                },
                                "answer": {
                                    "type": "string", 
                                    "description": "The answer to the riddle"
                                },
                                "explanation": {
                                    "type": "string",
                                    "description": "Educational explanation of the riddle and its answer"
                                }
                            },
                            "required": ["riddle", "answer", "explanation"],
                            "additionalProperties": False
                        }
                    }
                }
            )
            
            # Parse the response content as JSON
            content = response.choices[0].message.content
            return json.loads(content)
            
        except Exception as e:
            self.logger.error(f"OpenAI API error: {str(e)}")
            raise OpenAIError(f"Failed to generate completion: {str(e)}")
    
    def _parse_riddle_response(self, data: Dict[str, Any]) -> Dict[str, str]:
        """Parse and validate the riddle response.
        
        Args:
            data: The response data to parse
            
        Returns:
            The validated riddle data
            
        Raises:
            OpenAIError: If validation fails
        """
        try:
            # Validate required fields
            if not isinstance(data, dict):
                raise OpenAIError("Response is not a dictionary")
                
            required_fields = ["riddle", "answer", "explanation"]
            for field in required_fields:
                if field not in data:
                    raise OpenAIError(f"Missing required field '{field}'")
                
            # Validate field types
            for field in required_fields:
                if not isinstance(data[field], str):
                    raise OpenAIError(f"Field '{field}' must be a string")
                if not data[field].strip():
                    raise OpenAIError(f"Field '{field}' cannot be empty")
                
            # Return validated data
            return {
                "riddle": data["riddle"].strip(),
                "answer": data["answer"].strip(),
                "explanation": data["explanation"].strip()
            }
            
        except Exception as e:
            self.logger.error(f"Failed to parse riddle response: {str(e)}")
            raise OpenAIError(f"Invalid riddle data format: {str(e)}")
    
    def _validate_riddle(self, riddle_data: Dict[str, str]) -> bool:
        """Validate riddle data.
        
        Args:
            riddle_data: Dictionary with riddle and answer
            
        Returns:
            Whether the riddle is valid
        """
        try:
            # Check for required fields
            required_fields = ["riddle", "answer", "explanation"]
            for field in required_fields:
                if field not in riddle_data:
                    self.logger.debug(f"Missing field: {field}")
                    return False
            
            # Validate all fields are strings and not empty
            for field in required_fields:
                if not isinstance(riddle_data[field], str):
                    self.logger.debug(f"Field {field} is not a string")
                    return False
                if not riddle_data[field].strip():
                    self.logger.debug(f"Field {field} is empty")
                    return False
            
            # Check field lengths
            if len(riddle_data["riddle"]) < 10:
                self.logger.debug("Riddle text too short")
                return False
            
            if len(riddle_data["answer"]) < 1:
                self.logger.debug("Answer text too short")
                return False
            
            if len(riddle_data["explanation"]) < 10:
                self.logger.debug("Explanation text too short")
                return False
            
            # Check for inappropriate content
            if self._contains_inappropriate_content(riddle_data):
                self.logger.debug("Contains inappropriate content")
                return False
            
            return True
            
        except Exception as e:
            self.logger.debug(f"Validation error: {str(e)}")
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
    
    def _load_category_guidelines(self, category: str) -> str:
        """Load category-specific guidelines.
        
        Args:
            category: Riddle category
            
        Returns:
            Category guidelines
        """
        if category not in self.templates:
            raise ValueError(f"Invalid category: {category}")
            
        template = self.templates[category]
        guidelines = f"""System: {template['system_prompt']}
Example Format: {template['example_format']}"""
        
        return guidelines
    
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
        # Load category-specific guidelines
        guidelines = self._load_category_guidelines(category)
        
        # Format prompt
        prompt = f"""Create a {difficulty} {style} riddle about {category} for a {target_age} audience.

Category Guidelines:
{guidelines}

- Difficulty: {difficulty.capitalize()}
- Style: {style.capitalize()}
- Target Age: {target_age.capitalize()}
- Educational Content: {"Required" if educational else "Optional"}

The riddle should be engaging, appropriate, and follow the category guidelines.
Return your response as a JSON object with the following structure:
{{
    "riddle": "The riddle text",
    "answer": "The answer to the riddle"
}}"""
        
        return prompt

# Initialize global OpenAI service
config = Config()
openai_service = OpenAIService(config=config) 