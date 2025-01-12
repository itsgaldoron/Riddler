"""Configuration management"""

import os
import json
import logging
from typing import Any, Dict, Optional
from riddler.config.exceptions import ConfigurationError
from riddler.utils.logger import log
from riddler.utils.helpers import get_resource_path

class Configuration:
    """Configuration manager for the application."""
    
    def __init__(self, config_path: Optional[str] = None, logger: logging.Logger = None):
        """Initialize configuration."""
        self.logger = logger or log
        self.config: Dict[str, Any] = {}
        
        try:
            # Load default configuration from package resources
            default_config_path = get_resource_path("config.json")
            
            # Load default config if it exists
            if os.path.exists(default_config_path):
                with open(default_config_path, 'r') as f:
                    self.config = json.load(f)
            else:
                raise ConfigurationError(f"Default configuration not found at {default_config_path}")
            
            # Override with user config if provided
            if config_path and os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    user_config = json.load(f)
                    self.config.update(user_config)
                
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"Failed to parse configuration: {str(e)}")
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration: {str(e)}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)
