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
            log.info(f"Config key '{key}' not found, using default value: {default}")
            return default
    