# ⚙️ Configuration Management & Environment Setup

## The Configuration Philosophy

**Configuration should be separate from code** - this is one of the core principles of the [12-Factor App](https://12factor.net/config). Your FastAPI application demonstrates this perfectly through environment-based configuration management.

## How Configuration Works

### 1. **The Settings Class - Your Configuration Blueprint**

```python
class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    api_host: str = Field(default="0.0.0.0", description="API host address")
    api_port: int = Field(default=8000, description="API port number")
    debug: bool = Field(default=False, description="Enable debug mode")
```

**What Makes This Powerful:**

- **Type Safety**: `int`, `str`, `bool` ensure correct data types
- **Validation**: Pydantic validates values automatically
- **Documentation**: Field descriptions serve as inline documentation
- **Defaults**: Sensible fallbacks for development environments

### 2. **Environment Variable Hierarchy**

Your configuration follows this priority order (highest to lowest):

1. **Environment Variables** (e.g., `WINE_API_API_PORT=8080`)
2. **`.env` File** (local development overrides)
3. **Default Values** (defined in the Settings class)

```python
class Config:
    env_prefix = "WINE_API_"    # All env vars start with this
    case_sensitive = False       # WINE_API_DEBUG = wine_api_debug
    env_file = ".env"           # Load from .env file
```

### 3. **Configuration Categories Explained**

#### **API Configuration**
```python
api_host: str = Field(default="0.0.0.0")
api_port: int = Field(default=8000)
debug: bool = Field(default=False)
```

**Real-world usage:**
- **Development**: `debug=True` enables hot reloading
- **Production**: `api_host="0.0.0.0"` allows external connections
- **Testing**: Different ports avoid conflicts

#### **AWS Configuration**
```python
aws_region: str = Field(default="us-east-1")
s3_bucket_name: str = Field(default="mlops-processed-data-982248023588")
aws_access_key_id: Optional[str] = Field(default=None)
```

**Security Best Practices:**
- **IAM Roles Preferred**: `aws_access_key_id=None` uses instance roles
- **Environment Separation**: Different buckets for dev/staging/prod
- **Region Optimization**: Choose region closest to your users

#### **Model Configuration**
```python
model_path: str = Field(default="model.joblib")
model_cache_dir: str = Field(default="./model_cache")
model_cache_ttl: int = Field(default=3600)  # 1 hour
```

**Performance Implications:**
- **Local Caching**: Avoids repeated S3 downloads
- **TTL Strategy**: Balance freshness vs performance
- **Cache Directory**: Persistent storage across restarts

#### **Performance & Limits**
```python
max_request_size: int = Field(default=1024 * 1024)  # 1MB
request_timeout: int = Field(default=30)
rate_limit_requests: int = Field(default=100)
```

**Production Protection:**
- **Memory Protection**: Prevent huge requests from crashing service
- **Timeout Prevention**: Don't let slow requests hang indefinitely
- **Rate Limiting**: Protect against abuse and ensure fair usage

## Environment Setup Patterns

### **Development Environment (.env file)**
```bash
# .env file for local development
WINE_API_DEBUG=true
WINE_API_LOG_LEVEL=DEBUG
WINE_API_MODEL_CACHE_DIR=./dev_cache
WINE_API_AWS_REGION=us-east-1
```

**Benefits:**
- **Fast iteration**: Hot reloading with debug mode
- **Local testing**: Use local model cache
- **Safe defaults**: Won't affect production

### **Production Environment (Environment Variables)**
```bash
# Production environment variables
export WINE_API_DEBUG=false
export WINE_API_LOG_LEVEL=INFO
export WINE_API_API_HOST=0.0.0.0
export WINE_API_API_PORT=8000
export WINE_API_S3_BUCKET_NAME=prod-mlops-models
```

**Production Considerations:**
- **No .env files**: Use container environment variables
- **Secret management**: Use AWS Secrets Manager or similar
- **Monitoring**: Enable comprehensive logging

### **Testing Environment**
```bash
# Testing configuration
WINE_API_API_PORT=8001  # Different port to avoid conflicts
WINE_API_S3_BUCKET_NAME=test-mlops-models
WINE_API_MODEL_CACHE_TTL=60  # Shorter cache for testing
```

## Configuration Validation

### **Built-in Validation**
```python
def validate_configuration():
    """Validate critical configuration settings"""
    settings = get_settings()
    
    errors = []
    
    if not (1 <= settings.api_port <= 65535):
        errors.append(f"Invalid API port: {settings.api_port}")
    
    if not settings.s3_bucket_name:
        errors.append("S3 bucket name is required")
```

**Why Validation Matters:**
- **Fail Fast**: Catch configuration errors at startup
- **Clear Messages**: Help developers fix issues quickly
- **Production Safety**: Prevent misconfigured deployments

### **Advanced Configuration Features**

#### **Singleton Pattern**
```python
_settings = None

def get_settings() -> Settings:
    """Get application settings (singleton pattern)"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
```

**Benefits:**
- **Performance**: Configuration loaded once, reused everywhere
- **Consistency**: Same settings across all application components
- **Memory Efficiency**: Single instance instead of multiple copies

#### **AWS Configuration Factory**
```python
def get_aws_config() -> dict:
    """Get AWS configuration for boto3 clients"""
    settings = get_settings()
    
    config = {"region_name": settings.aws_region}
    
    if settings.aws_access_key_id and settings.aws_secret_access_key:
        config.update({
            "aws_access_key_id": settings.aws_access_key_id,
            "aws_secret_access_key": settings.aws_secret_access_key
        })
    
    return config
```

**Flexible Authentication:**
- **Development**: Use explicit credentials
- **Production**: Prefer IAM roles for security
- **Testing**: Use temporary credentials

## Configuration Management Best Practices

### **1. Environment Separation**
```
Development → .env file + defaults
Staging     → Environment variables + some overrides
Production  → Environment variables only
```

### **2. Secret Management**
```python
# ❌ Bad: Secrets in code
AWS_SECRET_KEY = "actual-secret-key"

# ✅ Good: Secrets in environment
aws_secret_access_key: Optional[str] = Field(default=None)
```

### **3. Configuration Documentation**
```python
model_cache_ttl: int = Field(
    default=3600,
    description="Model cache time-to-live in seconds",
    ge=0  # Greater than or equal to 0
)
```

### **4. Graceful Defaults**
```python
# Sensible defaults that work out of the box
api_host: str = Field(default="0.0.0.0")  # Accept all connections
api_port: int = Field(default=8000)        # Standard development port
debug: bool = Field(default=False)         # Production-safe default
```

## Real-World Deployment Examples

### **Docker Container**
```dockerfile
ENV WINE_API_API_HOST=0.0.0.0
ENV WINE_API_API_PORT=8000
ENV WINE_API_DEBUG=false
ENV WINE_API_S3_BUCKET_NAME=prod-models
```

### **Kubernetes Deployment**
```yaml
env:
  - name: WINE_API_API_PORT
    value: "8000"
  - name: WINE_API_S3_BUCKET_NAME
    valueFrom:
      configMapKeyRef:
        name: api-config
        key: s3-bucket
```

### **AWS ECS Task Definition**
```json
"environment": [
  {"name": "WINE_API_DEBUG", "value": "false"},
  {"name": "WINE_API_LOG_LEVEL", "value": "INFO"},
  {"name": "WINE_API_S3_BUCKET_NAME", "value": "production-models"}
]
```

## Configuration Testing Strategy

### **Unit Tests**
```python
def test_configuration_validation():
    """Test configuration validation logic"""
    # Test invalid port
    with pytest.raises(ValueError):
        settings = Settings(api_port=99999)
        validate_configuration()

def test_aws_config_with_credentials():
    """Test AWS configuration with explicit credentials"""
    settings = Settings(
        aws_access_key_id="test_key",
        aws_secret_access_key="test_secret"
    )
    config = get_aws_config()
    assert "aws_access_key_id" in config
```

### **Integration Tests**
```python
def test_environment_variable_override():
    """Test that environment variables override defaults"""
    os.environ["WINE_API_API_PORT"] = "9000"
    settings = Settings()
    assert settings.api_port == 9000
```

## Key Takeaways

### **Why This Configuration Strategy Works**

1. **Flexibility**: Same code works across all environments
2. **Security**: Secrets in environment variables, not code
3. **Validation**: Catch configuration errors early
4. **Documentation**: Self-documenting through Pydantic fields
5. **Type Safety**: Automatic type conversion and validation

### **Production Benefits**

- ✅ **Zero-downtime deployments**: Change config without code changes
- ✅ **Environment isolation**: Dev/staging/prod use different settings
- ✅ **Secret security**: Credentials never in source control
- ✅ **Monitoring integration**: Configuration-driven logging and metrics
- ✅ **Scalability**: Easy to adjust performance settings

---

*This configuration management approach enables professional deployment practices and operational excellence.*
