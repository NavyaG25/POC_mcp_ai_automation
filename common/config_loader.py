"""
Configuration loader for the automation framework.
Handles environment variables and configuration settings.
"""
import os
import logging
from dotenv import load_dotenv
from typing import Optional, Dict, Any

class ConfigLoader:
    """Centralized configuration management for UI and API tests."""
    
    _config_loaded = False
    _config = {}
    
    @classmethod
    def load_config(cls) -> Dict[str, Any]:
        """Load configuration from environment variables and .env file."""
        if cls._config_loaded:
            return cls._config
            
        try:
            # Load .env file
            env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
            load_dotenv(env_path)
            
            cls._config = {
                # UI Configuration
                'ui_base_url': os.getenv('UI_BASE_URL', 'https://automationintesting.online/'),
                'ui_admin_username': os.getenv('UI_ADMIN_USERNAME', 'admin'),
                'ui_admin_password': os.getenv('UI_ADMIN_PASSWORD', 'password'),
                
                # API Configuration
                'api_base_url': os.getenv('API_BASE_URL', 'https://restful-booker.herokuapp.com'),
                'api_username': os.getenv('API_USERNAME', 'admin'),
                'api_password': os.getenv('API_PASSWORD', 'password123'),
                
                # Test Configuration
                'browser_type': os.getenv('BROWSER_TYPE', 'chromium'),
                'headless': os.getenv('HEADLESS', 'false').lower() == 'true',
                'timeout': int(os.getenv('TIMEOUT', '30000')),
                'screenshot_on_failure': os.getenv('SCREENSHOT_ON_FAILURE', 'true').lower() == 'true'
            }
            
            cls._config_loaded = True
            logging.info("Configuration loaded successfully")
            
        except Exception as e:
            logging.warning(f"Failed to load .env file: {e}")
            # Provide default configuration if .env loading fails
            cls._config = {
                'ui_base_url': 'https://automationintesting.online/',
                'ui_admin_username': 'admin',
                'ui_admin_password': 'password',
                'api_base_url': 'https://restful-booker.herokuapp.com',
                'api_username': 'admin',
                'api_password': 'password123',
                'browser_type': 'chromium',
                'headless': False,
                'timeout': 30000,
                'screenshot_on_failure': True
            }
            cls._config_loaded = True
            
        return cls._config
    
    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """Get configuration value by key."""
        config = cls.load_config()
        return config.get(key, default)
    
    @classmethod
    def get_ui_config(cls) -> Dict[str, Any]:
        """Get UI-specific configuration."""
        config = cls.load_config()
        return {
            'base_url': config['ui_base_url'],
            'admin_username': config['ui_admin_username'],
            'admin_password': config['ui_admin_password'],
            'browser_type': config['browser_type'],
            'headless': config['headless'],
            'timeout': config['timeout']
        }
    
    @classmethod
    def get_api_config(cls) -> Dict[str, Any]:
        """Get API-specific configuration."""
        config = cls.load_config()
        return {
            'base_url': config['api_base_url'],
            'username': config['api_username'],
            'password': config['api_password']
        }
