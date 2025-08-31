"""
Configuration management for the FastAPI application

Handles environment variables, settings, and configuration validation.
Uses Pydantic BaseSettings for environment variable management.
"""

from pydantic import BaseSettings, Field
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # API Configuration
    api_host: str = Field(
        default="0.0.0.0",
        description="API host address"
    )
    
    api_port: int = Field(
        default=8000,
        description="API port number"
    )
    
    debug: bool = Field(
        default=False,
        description="Enable debug mode"
    )
    
    # AWS Configuration
    aws_region: str = Field(
        default="us-east-1",
        description="AWS region for S3 access"
    )
    
    s3_bucket_name: str = Field(
        default="mlops-processed-data-982248023588",
        description="S3 bucket containing model artifacts"
    )
    
    aws_access_key_id: Optional[str] = Field(
        default=None,
        description="AWS access key ID (optional, uses IAM roles if not provided)"
    )
    
    aws_secret_access_key: Optional[str] = Field(
        default=None,
        description="AWS secret access key (optional, uses IAM roles if not provided)"
    )
    
    # Model Configuration
    model_path: str = Field(
        default="model.joblib",
        description="S3 key/path to the model artifact"
    )
    
    model_cache_dir: str = Field(
        default="./model_cache",
        description="Local directory for model caching"
    )
    
    model_cache_ttl: int = Field(
        default=3600,  # 1 hour
        description="Model cache time-to-live in seconds"
    )
    
    # Application Configuration
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR)"
    )
    
    max_request_size: int = Field(
        default=1024 * 1024,  # 1MB
        description="Maximum request size in bytes"
    )
    
    request_timeout: int = Field(
        default=30,
        description="Request timeout in seconds"
    )
    
    # Health Check Configuration
    health_check_interval: int = Field(
        default=60,
        description="Health check interval in seconds"
    )
    
    # Rate Limiting (future implementation)
    rate_limit_requests: int = Field(
        default=100,
        description="Rate limit: requests per minute"
    )
    
    class Config:
        # Environment variable prefix
        env_prefix = "WINE_API_"
        
        # Case sensitivity for environment variables
        case_sensitive = False
        
        # Environment file support
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
_settings = None


def get_settings() -> Settings:
    """Get application settings (singleton pattern)"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def get_aws_config() -> dict:
    """Get AWS configuration for boto3 clients"""
    settings = get_settings()
    
    config = {
        "region_name": settings.aws_region
    }
    
    # Add credentials if provided (otherwise use IAM roles/environment)
    if settings.aws_access_key_id and settings.aws_secret_access_key:
        config.update({
            "aws_access_key_id": settings.aws_access_key_id,
            "aws_secret_access_key": settings.aws_secret_access_key
        })
    
    return config


def create_model_cache_dir():
    """Ensure model cache directory exists"""
    settings = get_settings()
    cache_dir = settings.model_cache_dir
    
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir, exist_ok=True)
        
    return cache_dir


# Configuration validation
def validate_configuration():
    """Validate critical configuration settings"""
    settings = get_settings()
    
    errors = []
    
    # Validate port range
    if not (1 <= settings.api_port <= 65535):
        errors.append(f"Invalid API port: {settings.api_port}")
    
    # Validate S3 bucket name
    if not settings.s3_bucket_name:
        errors.append("S3 bucket name is required")
    
    # Validate model path
    if not settings.model_path:
        errors.append("Model path is required")
    
    # Validate cache TTL
    if settings.model_cache_ttl < 0:
        errors.append("Model cache TTL must be non-negative")
    
    if errors:
        raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")
    
    return True


# Example environment variables file content
ENV_EXAMPLE = """
# Example .env file for Wine Quality Prediction API

# API Configuration
WINE_API_API_HOST=0.0.0.0
WINE_API_API_PORT=8000
WINE_API_DEBUG=false

# AWS Configuration
WINE_API_AWS_REGION=us-east-1
WINE_API_S3_BUCKET_NAME=mlops-processed-data-982248023588
# WINE_API_AWS_ACCESS_KEY_ID=your_access_key_here
# WINE_API_AWS_SECRET_ACCESS_KEY=your_secret_key_here

# Model Configuration
WINE_API_MODEL_PATH=model.joblib
WINE_API_MODEL_CACHE_DIR=./model_cache
WINE_API_MODEL_CACHE_TTL=3600

# Application Configuration
WINE_API_LOG_LEVEL=INFO
WINE_API_MAX_REQUEST_SIZE=1048576
WINE_API_REQUEST_TIMEOUT=30

# Health Check Configuration
WINE_API_HEALTH_CHECK_INTERVAL=60

# Rate Limiting
WINE_API_RATE_LIMIT_REQUESTS=100
"""
