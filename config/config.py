"""Configuration management"""

import os
import json
from typing import Any, Dict, Optional
from dataclasses import asdict
from config.schema import (
    ConfigSchema,
    OpenAIConfig,
    OpenAIRiddleGeneration,
    OpenAICommentaryGeneration,
    OpenAIDifficultyLevel,
    OpenAIRiddleTemplate
)
from config.exceptions import ConfigValidationError
from utils.logger import log

class Config:
    """Configuration manager"""
    
    def __init__(self, config_path: str = "config/config.json"):
        """Initialize configuration
        
        Args:
            config_path: Path to config file
        """
        self.config_path = config_path
        self.config = {}
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r") as f:
                    self.config = json.load(f)
            else:
                self.config = ConfigSchema.get_default_config()
                self.save_config()
        except Exception as e:
            log.error(f"Error loading config: {e}")
            self.config = ConfigSchema.get_default_config()
    
    def save_config(self) -> None:
        """Save configuration to file"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, "w") as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            log.error(f"Error saving config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value
        
        Args:
            key: Configuration key (dot notation)
            default: Default value if not found
            
        Returns:
            Configuration value
        """
        try:
            value = self.config
            for k in key.split("."):
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value
        
        Args:
            key: Configuration key (dot notation)
            value: Value to set
            
        Raises:
            ValueError: If value is invalid
        """
        # Split key into parts
        keys = key.split(".")
        
        # Navigate to the correct level
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
        
        # Validate after setting
        try:
            self.validate()
        except ValueError as e:
            # Revert change if validation fails
            self.load_config()
            raise ValueError(f"Invalid configuration value: {e}")
        
        self.save_config()
    
    def validate(self) -> bool:
        """Validate configuration
        
        Returns:
            True if valid
            
        Raises:
            ValueError: If configuration is invalid
        """
        try:
            # Convert OpenAI configuration to proper objects
            if "openai" in self.config:
                openai_config = self.config["openai"]
                
                # Convert difficulty levels
                if "riddle_generation" in openai_config:
                    riddle_gen = openai_config["riddle_generation"]
                    if "difficulty_levels" in riddle_gen:
                        difficulty_levels = {}
                        for level, data in riddle_gen["difficulty_levels"].items():
                            difficulty_levels[level] = OpenAIDifficultyLevel(**data)
                        riddle_gen["difficulty_levels"] = difficulty_levels
                    
                    # Convert templates
                    if "templates" in riddle_gen:
                        templates = {}
                        for name, data in riddle_gen["templates"].items():
                            templates[name] = OpenAIRiddleTemplate(**data)
                        riddle_gen["templates"] = templates
                    
                    # Create OpenAIRiddleGeneration object
                    openai_config["riddle_generation"] = OpenAIRiddleGeneration(**riddle_gen)
                
                # Convert commentary generation
                if "commentary_generation" in openai_config:
                    commentary_gen = openai_config["commentary_generation"]
                    openai_config["commentary_generation"] = OpenAICommentaryGeneration(**commentary_gen)
                
                # Create OpenAIConfig object
                self.config["openai"] = OpenAIConfig(**openai_config)
            
            # Validate using schema
            ConfigSchema(**self.config).validate(self.config)
            
            return True
            
        except Exception as e:
            log.warning(f"Configuration validation failed: {str(e)}")
            return False
    
    def reset(self) -> None:
        """Reset configuration to defaults"""
        self.config = ConfigSchema.get_default_config()
        self.save_config()
    
    def merge(self, other_config: Dict[str, Any]) -> None:
        """Merge another configuration
        
        Args:
            other_config: Configuration to merge
        """
        def deep_merge(source: Dict[str, Any], destination: Dict[str, Any]) -> Dict[str, Any]:
            for key, value in source.items():
                if key in destination:
                    if isinstance(value, dict) and isinstance(destination[key], dict):
                        deep_merge(value, destination[key])
                    else:
                        destination[key] = value
                else:
                    destination[key] = value
            return destination
        
        self.config = deep_merge(other_config, self.config)
        self.validate()
        self.save_config() 