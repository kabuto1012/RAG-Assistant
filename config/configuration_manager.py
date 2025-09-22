"""
Configuration management for the RDR2 Agent system.
Implements the Single Responsibility Principle by handling only configuration-related tasks.
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from models.base_models import IConfigurationManager


class ConfigurationManager(IConfigurationManager):
    """
    Concrete implementation of configuration management.
    only handles configuration.
    """
    
    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()
        
        self._config: Dict[str, Any] = {}
        self._api_keys: Dict[str, str] = {}
        self._llm_configs: Dict[str, Dict[str, Any]] = {}
        self._initialize_default_config()
    
    def _initialize_default_config(self) -> None:
        """Initialize default configuration values."""
        # Load API keys from environment variables only - no hardcoded fallbacks
        self._api_keys = {
            "gemini": os.environ.get("GEMINI_API_KEY"),
            "agentops": os.environ.get("AGENTOPS_API_KEY"),
            "serper": os.environ.get("SERPER_API_KEY")
        }
        
        # Validate that required API keys are present
        for service, key in self._api_keys.items():
            if not key:
                raise ValueError(f"Missing required API key for {service}. Please set {service.upper()}_API_KEY environment variable.")
        
        # Default LLM configurations
        self._llm_configs = {
            "gemini-pro": {
                "model": "gemini/gemini-2.5-pro",
                "temperature": 0.0,
                "api_key_name": "gemini"
            },
            "gemini-flash": {
                "model": "gemini/gemini-2.0-flash", 
                "temperature": 0.0,
                "api_key_name": "gemini"
            }
        }
        
        # General configuration
        self._config = {
            "knowledge_base_path": "info",
            "chroma_db_path": "./chroma_db",
            "embedding_model": "all-MiniLM-L6-v2",
            "search_top_n": 5,
            "relevance_threshold": 2.2,
            "excluded_domains": ["reddit.com", "quora.com", "youtube.com", "steamcommunity.com"]
        }
    
    def get_api_key(self, service: str) -> str:
        """
        Get API key for a specific service.
        
        Args:
            service: Name of the service (e.g., 'gemini', 'agentops', 'serper')
            
        Returns:
            str: The API key for the service
            
        Raises:
            KeyError: If the service is not configured
        """
        if service not in self._api_keys:
            raise KeyError(f"API key for service '{service}' not found")
        return self._api_keys[service]
    
    def get_llm_config(self, model_name: str) -> Dict[str, Any]:
        """
        Get configuration for a specific LLM model.
        
        Args:
            model_name: Name of the model (e.g., 'gemini-pro', 'gemini-flash')
            
        Returns:
            Dict[str, Any]: Configuration dictionary for the model
            
        Raises:
            KeyError: If the model is not configured
        """
        if model_name not in self._llm_configs:
            raise KeyError(f"LLM configuration for '{model_name}' not found")
        
        config = self._llm_configs[model_name].copy()
        # Replace api_key_name with actual API key
        if "api_key_name" in config:
            api_key_name = config.pop("api_key_name")
            config["api_key"] = self.get_api_key(api_key_name)
        
        return config
    
    def load_configuration(self, config_path: Optional[str] = None) -> bool:
        """
        Load configuration from file or environment.
        For now, we're using default configuration, but this can be extended
        to load from JSON/YAML files.
        
        Args:
            config_path: Path to configuration file (optional)
            
        Returns:
            bool: True if configuration loaded successfully
        """
        try:
            # Validate that all required API keys are present
            for service, key in self._api_keys.items():
                if not key:
                    raise ValueError(f"Missing required API key for {service}")
            
            return True
        except Exception as e:
            print(f"Error loading configuration: {e}")
            return False
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        """
        Get a general configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Any: Configuration value
        """
        return self._config.get(key, default)
    
    def set_config_value(self, key: str, value: Any) -> None:
        """
        Set a configuration value.
        
        Args:
            key: Configuration key
            value: Configuration value
        """
        self._config[key] = value
    
    def get_knowledge_base_path(self) -> str:
        """Get the path to the knowledge base."""
        return self._config["knowledge_base_path"]
    
    def get_chroma_db_path(self) -> str:
        """Get the path to the ChromaDB database."""
        return self._config["chroma_db_path"]
    
    def get_embedding_model(self) -> str:
        """Get the name of the embedding model."""
        return self._config["embedding_model"]
    
    def get_search_top_n(self) -> int:
        """Get the number of top search results to return."""
        return self._config["search_top_n"]
    
    def get_relevance_threshold(self) -> float:
        """Get the relevance threshold for search results."""
        return self._config["relevance_threshold"]
    
    def get_excluded_domains(self) -> list:
        """Get the list of domains to exclude from web searches."""
        return self._config["excluded_domains"].copy()
