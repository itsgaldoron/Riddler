"""Service for generating riddles and related content."""

from pathlib import Path
from typing import Optional, List, Dict, Any, Union, Tuple
import json
import random
from utils.logger import log
from utils.cache import cache
from utils.helpers import (
    ensure_directory,
    generate_cache_key,
    format_timestamp,
    parse_timestamp
)
from config.exceptions import RiddlerException

class RiddleService:
    """Service for generating riddles and related content."""
    
    def __init__(
        self,
        cache_dir: str = "cache/riddles",
        openai_model: str = "gpt-4",
        max_attempts: int = 3,
        temperature: float = 0.7
    ):
        """Initialize riddle service.
        
        Args:
            cache_dir: Directory for cached riddles
            openai_model: OpenAI model to use
            max_attempts: Maximum generation attempts
            temperature: Generation temperature
        """
        self.cache_dir = Path(cache_dir)
        self.openai_model = openai_model
        self.max_attempts = max_attempts
        self.temperature = temperature
        
        # Create directories
        ensure_directory(self.cache_dir)
        
        # Load system prompts
        self.system_prompts = {
            "riddle": self._load_system_prompt("riddle"),
            "educational": self._load_system_prompt("educational"),
            "commentary": self._load_system_prompt("commentary"),
            "fun_facts": self._load_system_prompt("fun_facts")
        }
        
    def _load_system_prompt(self, prompt_type: str) -> str:
        """Load system prompt from file.
        
        Args:
            prompt_type: Type of prompt to load
            
        Returns:
            System prompt text
        """
        prompt_path = Path("prompts") / f"{prompt_type}.txt"
        if not prompt_path.exists():
            return self._get_default_prompt(prompt_type)
            
        return prompt_path.read_text()
        
    def _get_default_prompt(self, prompt_type: str) -> str:
        """Get default system prompt.
        
        Args:
            prompt_type: Type of prompt
            
        Returns:
            Default system prompt
        """
        prompts = {
            "riddle": """You are an expert riddle creator. Your goal is to create 
                engaging, clever riddles that are challenging but solvable. The 
                riddles should be:
                - Clear and unambiguous
                - Appropriate for the target audience
                - Free of offensive content
                - Educational when possible
                - Culturally relevant
                Format: Return a JSON object with 'riddle' and 'answer' fields.""",
                
            "educational": """You are an educational content creator. Your goal is
                to create engaging, informative content that:
                - Explains concepts clearly
                - Uses age-appropriate language
                - Includes relevant examples
                - Connects to real-world applications
                - Encourages critical thinking
                Format: Return a JSON object with 'content' and 'difficulty' fields.""",
                
            "commentary": """You are a witty commentator. Your goal is to create
                engaging commentary that:
                - Adds humor and personality
                - Provides interesting context
                - Maintains audience engagement
                - Reinforces learning
                - Varies in tone and style
                Format: Return a JSON object with 'intro', 'reveal', and 'outro' fields.""",
                
            "fun_facts": """You are a fun fact expert. Your goal is to share
                interesting facts that:
                - Relate to the main topic
                - Surprise and delight
                - Encourage further learning
                - Are memorable
                - Are verified and accurate
                Format: Return a JSON object with 'facts' array and 'sources' array."""
        }
        
        return prompts.get(prompt_type, "")
        
    def generate_riddle(
        self,
        category: str,
        difficulty: str = "medium",
        style: str = "classic",
        target_age: str = "teen",
        educational: bool = True,
        cache_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate a riddle.
        
        Args:
            category: Riddle category
            difficulty: Difficulty level
            style: Riddle style
            target_age: Target age group
            educational: Whether to include educational content
            cache_key: Optional cache key
            
        Returns:
            Dictionary with riddle content
        """
        try:
            # Generate cache key if not provided
            if not cache_key:
                cache_key = generate_cache_key(
                    "riddle",
                    category=category,
                    difficulty=difficulty,
                    style=style,
                    target_age=target_age
                )
                
            # Check cache
            cached_path = self.cache_dir / f"{cache_key}.json"
            if cached_path.exists():
                return json.loads(cached_path.read_text())
                
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
                        "riddle",
                        temperature=self.temperature + (attempt * 0.1)
                    )
                    
                    # Parse and validate response
                    content = self._parse_riddle_response(response)
                    if self._validate_riddle(content):
                        break
                except Exception as e:
                    if attempt == self.max_attempts - 1:
                        raise
                    continue
                    
            # Add metadata
            content.update({
                "category": category,
                "difficulty": difficulty,
                "style": style,
                "target_age": target_age
            })
            
            # Cache result
            cached_path.write_text(json.dumps(content, indent=2))
            
            return content
            
        except Exception as e:
            raise RiddlerException(f"Failed to generate riddle: {str(e)}")
            
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

Additional Requirements:
- Difficulty: {difficulty.capitalize()}
- Style: {style.capitalize()}
- Target Age: {target_age.capitalize()}
- Educational Content: {"Required" if educational else "Optional"}

The riddle should be engaging, appropriate, and follow the category guidelines.
"""
        
        return prompt
        
    def _load_category_guidelines(self, category: str) -> str:
        """Load category-specific guidelines.
        
        Args:
            category: Riddle category
            
        Returns:
            Category guidelines
        """
        guidelines = {
            "math": """
                - Use mathematical concepts appropriate for the target age
                - Include word problems that require logical thinking
                - Avoid complex notation or advanced concepts
                - Make connections to real-world applications
                - Encourage mental math and estimation
            """,
            
            "science": """
                - Focus on fundamental scientific principles
                - Use accurate but accessible terminology
                - Include observable phenomena
                - Connect to everyday experiences
                - Promote scientific curiosity
            """,
            
            "nature": """
                - Feature plants, animals, or natural phenomena
                - Include interesting biological facts
                - Highlight environmental connections
                - Use descriptive, vivid language
                - Promote appreciation for nature
            """,
            
            "history": """
                - Focus on significant historical events or figures
                - Include interesting but lesser-known facts
                - Make connections to the present
                - Avoid controversial topics
                - Promote historical understanding
            """,
            
            "technology": """
                - Focus on common technology concepts
                - Include modern and relevant examples
                - Avoid overly technical language
                - Make connections to daily life
                - Promote digital literacy
            """
        }
        
        return guidelines.get(
            category,
            "- Keep content appropriate and engaging\n- Follow general riddle best practices"
        )
        
    def _generate_completion(
        self,
        prompt: str,
        prompt_type: str,
        temperature: float
    ) -> str:
        """Generate completion using OpenAI API.
        
        Args:
            prompt: Input prompt
            prompt_type: Type of prompt
            temperature: Generation temperature
            
        Returns:
            Generated text
        """
        try:
            import os
            from openai import OpenAI
            
            # Initialize client with API key from environment
            client = OpenAI(
                api_key=os.environ.get("RIDDLER_OPENAI_API_KEY"),
            )
            
            # Create messages
            messages = [
                {
                    "role": "system",
                    "content": self.system_prompts[prompt_type]
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            
            # Generate completion
            response = client.chat.completions.create(
                model=self.openai_model,
                messages=messages,
                temperature=temperature,
                max_tokens=500,
                n=1
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise RiddlerException(f"Failed to generate completion: {str(e)}")
            
    def _parse_riddle_response(self, response: str) -> Dict[str, Any]:
        """Parse riddle response.
        
        Args:
            response: Raw response text
            
        Returns:
            Parsed content dictionary
        """
        try:
            # Extract JSON from response
            start = response.find("{")
            end = response.rfind("}") + 1
            
            if start == -1 or end == 0:
                raise ValueError("No JSON object found in response")
                
            json_str = response[start:end]
            content = json.loads(json_str)
            
            # Validate required fields
            required_fields = ["riddle", "answer"]
            missing_fields = [
                field for field in required_fields
                if field not in content
            ]
            
            if missing_fields:
                raise ValueError(
                    f"Missing required fields: {', '.join(missing_fields)}"
                )
                
            return content
            
        except Exception as e:
            raise RiddlerException(f"Failed to parse response: {str(e)}")
            
    def _validate_riddle(self, content: Dict[str, Any]) -> bool:
        """Validate riddle content.
        
        Args:
            content: Riddle content dictionary
            
        Returns:
            Whether content is valid
        """
        try:
            # Check for empty values
            if not content["riddle"] or not content["answer"]:
                return False
                
            # Check length constraints
            if len(content["riddle"]) > 200 or len(content["answer"]) > 50:
                return False
                
            # Check for inappropriate content
            if self._contains_inappropriate_content(content):
                return False
                
            # Additional validation can be added here
            
            return True
            
        except Exception:
            return False
            
    def _contains_inappropriate_content(
        self,
        content: Dict[str, Any]
    ) -> bool:
        """Check for inappropriate content.
        
        Args:
            content: Content to check
            
        Returns:
            Whether content is inappropriate
        """
        # Load inappropriate words list
        bad_words_path = Path("config/bad_words.txt")
        if bad_words_path.exists():
            bad_words = set(bad_words_path.read_text().splitlines())
        else:
            bad_words = set()  # Default to empty set
            
        # Check all text fields
        text = " ".join(str(v) for v in content.values()).lower()
        
        return any(word in text for word in bad_words)
        
    def generate_educational_content(
        self,
        topic: str,
        category: str,
        difficulty: str = "medium",
        target_age: str = "teen",
        cache_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate educational content.
        
        Args:
            topic: Content topic
            category: Content category
            difficulty: Difficulty level
            target_age: Target age group
            cache_key: Optional cache key
            
        Returns:
            Dictionary with educational content
        """
        try:
            # Generate cache key if not provided
            if not cache_key:
                cache_key = generate_cache_key(
                    "educational",
                    topic=topic,
                    category=category,
                    difficulty=difficulty,
                    target_age=target_age
                )
                
            # Check cache
            cached_path = self.cache_dir / f"{cache_key}.json"
            if cached_path.exists():
                return json.loads(cached_path.read_text())
                
            # Prepare prompt
            prompt = f"""Create educational content about {topic} in the {category} category.

Requirements:
- Difficulty: {difficulty.capitalize()}
- Target Age: {target_age.capitalize()}
- Include clear explanations
- Use engaging examples
- Connect to real-world applications
"""
            
            # Generate content
            response = self._generate_completion(
                prompt,
                "educational",
                temperature=self.temperature
            )
            
            # Parse response
            content = json.loads(response)
            
            # Add metadata
            content.update({
                "topic": topic,
                "category": category,
                "difficulty": difficulty,
                "target_age": target_age
            })
            
            # Cache result
            cached_path.write_text(json.dumps(content, indent=2))
            
            return content
            
        except Exception as e:
            raise RiddlerException(f"Failed to generate educational content: {str(e)}")
            
    def generate_commentary(
        self,
        riddle: Dict[str, Any],
        style: str = "witty",
        cache_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate commentary for a riddle.
        
        Args:
            riddle: Riddle content dictionary
            style: Commentary style
            cache_key: Optional cache key
            
        Returns:
            Dictionary with commentary content
        """
        try:
            # Generate cache key if not provided
            if not cache_key:
                cache_key = generate_cache_key(
                    "commentary",
                    riddle=riddle["riddle"],
                    answer=riddle["answer"],
                    style=style
                )
                
            # Check cache
            cached_path = self.cache_dir / f"{cache_key}.json"
            if cached_path.exists():
                return json.loads(cached_path.read_text())
                
            # Prepare prompt
            prompt = f"""Create {style} commentary for this riddle:

Riddle: {riddle["riddle"]}
Answer: {riddle["answer"]}
Category: {riddle.get("category", "unknown")}
Difficulty: {riddle.get("difficulty", "medium")}

Requirements:
- Style: {style.capitalize()}
- Include introduction
- Build suspense
- Create satisfying reveal
- Add interesting context
"""
            
            # Generate commentary
            response = self._generate_completion(
                prompt,
                "commentary",
                temperature=self.temperature
            )
            
            # Parse response
            content = json.loads(response)
            
            # Add metadata
            content.update({
                "style": style,
                "riddle_id": riddle.get("id")
            })
            
            # Cache result
            cached_path.write_text(json.dumps(content, indent=2))
            
            return content
            
        except Exception as e:
            raise RiddlerException(f"Failed to generate commentary: {str(e)}")
            
    def generate_fun_facts(
        self,
        topic: str,
        category: str,
        num_facts: int = 3,
        cache_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate fun facts about a topic.
        
        Args:
            topic: Topic for fun facts
            category: Fact category
            num_facts: Number of facts to generate
            cache_key: Optional cache key
            
        Returns:
            Dictionary with fun facts content
        """
        try:
            # Generate cache key if not provided
            if not cache_key:
                cache_key = generate_cache_key(
                    "fun_facts",
                    topic=topic,
                    category=category,
                    num_facts=num_facts
                )
                
            # Check cache
            cached_path = self.cache_dir / f"{cache_key}.json"
            if cached_path.exists():
                return json.loads(cached_path.read_text())
                
            # Prepare prompt
            prompt = f"""Generate {num_facts} interesting facts about {topic} in the {category} category.

Requirements:
- Include surprising information
- Verify accuracy
- Cite sources
- Make facts memorable
- Connect to the main topic
"""
            
            # Generate facts
            response = self._generate_completion(
                prompt,
                "fun_facts",
                temperature=self.temperature
            )
            
            # Parse response
            content = json.loads(response)
            
            # Add metadata
            content.update({
                "topic": topic,
                "category": category,
                "num_facts": num_facts
            })
            
            # Cache result
            cached_path.write_text(json.dumps(content, indent=2))
            
            return content
            
        except Exception as e:
            raise RiddlerException(f"Failed to generate fun facts: {str(e)}")

# Initialize global riddle service
riddle_service = RiddleService() 