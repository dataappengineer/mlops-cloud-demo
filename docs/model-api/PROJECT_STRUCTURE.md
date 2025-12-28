# 📋 Project Structure & Design Decisions

## Architecture Overview

Our Wine Quality Prediction API follows a **layered architecture pattern** that separates concerns and makes the codebase maintainable and scalable.

## Directory Structure Explained

### Core Application (`app/`)

```
app/
├── __init__.py           # Package initialization
├── main.py              # Application entry point & routing
├── models/              # Data models & validation
├── services/            # Business logic layer  
└── utils/               # Cross-cutting concerns
```

#### Design Principle: **Separation of Concerns**
Each directory has a specific responsibility, making the code:
- **Easier to test**: Each layer can be tested independently
- **Easier to maintain**: Changes in one layer don't affect others
- **Easier to scale**: Can replace implementations without affecting interfaces

### Layer Details

#### 1. **Entry Point Layer** (`main.py`)
**Purpose**: Handle HTTP communication and API routing

**Responsibilities**:
- Define API endpoints and HTTP methods
- Configure middleware (CORS, logging, etc.)
- Handle HTTP-specific concerns (status codes, headers)
- Route requests to appropriate services
- Format responses for clients

**Why separate this?**: Keeps HTTP concerns separate from business logic

#### 2. **Data Model Layer** (`models/`)
**Purpose**: Define data structures and validation rules

**Responsibilities**:
- Input validation (ensure data is correct format)
- Output formatting (standardize response structure)
- Type safety (catch errors early)
- API documentation (auto-generate from models)

**Why separate this?**: Ensures data integrity and API contract consistency

#### 3. **Service Layer** (`services/`)
**Purpose**: Implement core business logic

**Responsibilities**:
- Model loading and management
- Prediction algorithms
- External integrations (S3, databases)
- Caching strategies
- Error handling for business logic

**Why separate this?**: Makes business logic reusable and testable

#### 4. **Utility Layer** (`utils/`)
**Purpose**: Provide shared functionality

**Responsibilities**:
- Configuration management
- Logging setup
- Helper functions
- Constants and enums

**Why separate this?**: Avoid code duplication and centralize common concerns

## Configuration Strategy

### Environment-Based Configuration
```python
# Development
DEBUG=True
MODEL_PATH=./local_model.joblib

# Production  
DEBUG=False
MODEL_PATH=s3://bucket/model.joblib
```

**Benefits**:
- Same code works in different environments
- Secrets kept out of source code
- Easy to change behavior without code changes

### Configuration Files Hierarchy
1. **`.env.example`**: Template showing required variables
2. **`.env`**: Local development overrides (git-ignored)
3. **Environment variables**: Production configuration
4. **Default values**: Fallbacks in code

## Development Workflow

### Local Development
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set up environment
cp .env.example .env

# 3. Run development server
python run_dev.py
```

### Containerized Development
```bash
# Build and run with Docker
docker-compose up --build
```

### Testing
```bash
# Run API tests
python test_api.py
```

## Design Patterns Used

### 1. **Dependency Injection**
Services are injected into endpoints, making testing easier:
```python
@app.post("/predict")
async def predict(request: WineFeaturesRequest, service: ModelService = Depends()):
    return service.predict(request.features)
```

### 2. **Factory Pattern**
Configuration and services are created using factory functions:
```python
def get_settings() -> Settings:
    return Settings()

def get_model_service() -> ModelService:
    return ModelService(get_settings())
```

### 3. **Repository Pattern**
Model loading abstracted behind an interface:
```python
class ModelService:
    def load_model(self) -> Model:
        # Can load from S3, local file, database, etc.
        pass
```

## Error Handling Strategy

### Three-Layer Error Handling
1. **Validation Layer**: Catch malformed requests
2. **Service Layer**: Handle business logic errors  
3. **Global Handler**: Catch unexpected errors

### Error Response Format
```json
{
    "error": true,
    "message": "Human-readable error message",
    "details": "Technical details for debugging",
    "timestamp": "2025-08-31T10:00:00Z"
}
```

## Scalability Considerations

### Horizontal Scaling
- **Stateless design**: No server-side session storage
- **Database connections**: Use connection pooling
- **Caching**: Model cached in memory, shared cache for multiple instances

### Performance Optimizations
- **Async endpoints**: Handle multiple requests concurrently
- **Model caching**: Avoid reloading model for each request
- **Response compression**: Reduce network bandwidth
- **Health checks**: Enable load balancer management

## Security Considerations

### Input Validation
- **Type checking**: Pydantic models enforce types
- **Range validation**: Realistic value ranges for wine features
- **Sanitization**: Clean input data before processing

### CORS Configuration
- **Development**: Allow all origins for testing
- **Production**: Restrict to known domains

### Secrets Management
- **Environment variables**: Keep secrets out of code
- **AWS credentials**: Use IAM roles in production
- **API keys**: Rotate regularly

---

*This structure enables rapid development while maintaining production-quality standards.*
