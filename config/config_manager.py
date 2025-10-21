"""
Configuration Manager for AI Agent Workflow System
Handles loading and validation of configuration settings
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages configuration settings for the AI Agent Workflow System"""
    
    def __init__(self, config_path: str = "config/config.json"):
        """
        Initialize the configuration manager
        
        Args:
            config_path: Path to the configuration file
        """
        self.config_path = Path(config_path)
        # Load environment variables from .env file
        load_dotenv()
        self.config: Dict[str, Any] = {}
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from JSON file"""
        try:
            if not self.config_path.exists():
                logger.warning(f"Config file not found at {self.config_path}")
                self.create_default_config()
                return
            
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            
            logger.info("Configuration loaded successfully")
            self.validate_config()
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            raise
    
    def create_default_config(self) -> None:
        """Create a default configuration file"""
        default_config = {
            "gemini": {
                "api_key": "your-gemini-api-key-here",
                "model": "gemini-pro",
                "temperature": 0.7,
                "max_tokens": 1000
            },
            "hubspot": {
                "api_key": "your-hubspot-api-key-here",
                "base_url": "https://api.hubapi.com"
            },
            "email": {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "your-email@gmail.com",
                "password": "your-app-password-here"
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        }
        
        # Ensure config directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=4)
        
        logger.info(f"Default configuration created at {self.config_path}")
        self.config = default_config
    
    def validate_config(self) -> None:
        """Validate that required configuration keys are present"""
        required_sections = ["gemini", "hubspot", "email", "logging"]
        
        for section in required_sections:
            if section not in self.config:
                logger.error(f"Missing required configuration section: {section}")
                raise ValueError(f"Missing required configuration section: {section}")
        
        # Validate Gemini config
        if not self.config["gemini"].get("api_key") or self.config["gemini"]["api_key"].startswith("your-"):
            logger.warning("Gemini API key not configured")
        
        # Validate HubSpot config
        if not self.config["hubspot"].get("api_key") or self.config["hubspot"]["api_key"].startswith("your-"):
            logger.warning("HubSpot API key not configured")
        
        # Validate email config
        if not self.config["email"].get("username") or self.config["email"]["username"].startswith("your-"):
            logger.warning("Email credentials not configured")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation with environment variable fallback
        
        Args:
            key: Configuration key (e.g., 'gemini.api_key')
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        # First try to get from environment variables
        env_key = key.upper().replace('.', '_')
        env_value = os.getenv(env_key)
        
        # Handle special mappings for email configuration
        if key == "email.username" and not env_value:
            env_value = os.getenv("SMTP_USER") or os.getenv("EMAIL_USERNAME")
        elif key == "email.password" and not env_value:
            env_value = os.getenv("SMTP_PASS") or os.getenv("EMAIL_PASSWORD")
        elif key == "email.smtp_server" and not env_value:
            env_value = os.getenv("SMTP_HOST")
        elif key == "email.smtp_port" and not env_value:
            env_value = os.getenv("SMTP_PORT")
        
        if env_value:
            return env_value
        
        # Fallback to config file
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_gemini_config(self) -> Dict[str, Any]:
        """Get Gemini configuration"""
        gemini_config = self.config.get("gemini", {}).copy()
        
        # Override with environment variables if available
        if os.getenv("GEMINI_API_KEY"):
            gemini_config["api_key"] = os.getenv("GEMINI_API_KEY")
        
        return gemini_config
    
    def get_hubspot_config(self) -> Dict[str, Any]:
        """Get HubSpot configuration"""
        return self.config.get("hubspot", {})
    
    def get_email_config(self) -> Dict[str, Any]:
        """Get email configuration"""
        return self.config.get("email", {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration"""
        return self.config.get("logging", {})
    
    def is_configured(self) -> bool:
        """Check if all required credentials are configured"""
        gemini_key = self.get("gemini.api_key", "")
        hubspot_key = self.get("hubspot.api_key", "")
        email_user = self.get("email.username", "")
        
        return (
            gemini_key and not gemini_key.startswith("your-") and
            hubspot_key and not hubspot_key.startswith("your-") and
            email_user and not email_user.startswith("your-")
        )
