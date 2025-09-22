"""
Production configuration for the RDR2 Agent API.
Environment-specific settings for deployment.
"""

import os
from typing import List, Dict, Any


class ProductionConfig:
    """Production configuration settings."""
    
    # API Configuration
    API_TITLE = "RDR2 Agent API"
    API_VERSION = "1.0.0"
    API_DESCRIPTION = "Production-ready API for Red Dead Redemption 2 intelligent assistant"
    
    # Server Configuration
    HOST = os.getenv("API_HOST", "0.0.0.0")
    PORT = int(os.getenv("API_PORT", "8000"))
    
    # Security Configuration
    ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
    
    # Rate Limiting (requests per minute)
    RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "60"))
    RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # seconds
    
    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Request Limits
    MAX_QUERY_LENGTH = int(os.getenv("MAX_QUERY_LENGTH", "1000"))
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "60"))  # seconds
    
    # Health Check Configuration
    HEALTH_CHECK_TIMEOUT = int(os.getenv("HEALTH_CHECK_TIMEOUT", "30"))
    
    @classmethod
    def get_cors_config(cls) -> Dict[str, Any]:
        """Get CORS configuration for FastAPI."""
        return {
            "allow_origins": cls.CORS_ORIGINS,
            "allow_credentials": True,
            "allow_methods": ["GET", "POST"],
            "allow_headers": ["*"],
        }
    
    @classmethod
    def get_trusted_hosts(cls) -> List[str]:
        """Get trusted hosts configuration."""
        return cls.ALLOWED_HOSTS
    
    @classmethod
    def is_development(cls) -> bool:
        """Check if running in development mode."""
        return os.getenv("ENVIRONMENT", "production").lower() == "development"


class DevelopmentConfig(ProductionConfig):
    """Development configuration settings."""
    
    # Override for development
    HOST = "127.0.0.1"
    ALLOWED_HOSTS = ["*"]
    CORS_ORIGINS = ["*"]
    LOG_LEVEL = "DEBUG"
    
    @classmethod
    def is_development(cls) -> bool:
        return True


def get_config() -> ProductionConfig:
    """
    Get the appropriate configuration based on environment.
    
    Returns:
        ProductionConfig: Configuration instance
    """
    env = os.getenv("ENVIRONMENT", "production").lower()
    
    if env == "development":
        return DevelopmentConfig()
    else:
        return ProductionConfig()
