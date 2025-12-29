# MLOps Model API

A production-ready FastAPI service for serving the trained wine quality prediction model with S3 integration, comprehensive monitoring, and Docker deployment.

## 🎯 Overview

This API serves the machine learning model trained by our Airflow pipeline, providing:
- **Real-time predictions** via REST endpoints
- **S3 integration** for model loading and versioning
- **Production monitoring** with health checks and metrics
- **Docker deployment** for scalable containerized deployment
- **Comprehensive documentation** with automatic OpenAPI specs

## 🏗️ Architecture

```
model-api/
├── app/
│   ├── main.py              # FastAPI application
│   ├── models/
│   │   └── prediction.py    # Pydantic models for request/response
│   ├── services/
│   │   └── model_service.py # Model loading and prediction logic
│   └── utils/
│       └── config.py        # Configuration management
├── Dockerfile               # Container configuration
├── docker-compose.yml       # Multi-service deployment
├── requirements.txt         # Python dependencies
├── test_api.py             # API testing script
└── run_dev.py              # Development server
```

## 🚀 Quick Start

### Local Development

1. **Install dependencies:**
   ```bash
   cd model-api
   pip install -r requirements.txt
   ```

2. **Configure AWS credentials:**
   ```bash
   aws configure
   # or set environment variables:
   export AWS_PROFILE=default
   export AWS_DEFAULT_REGION=us-east-1
   export S3_BUCKET_NAME=mlops-demo-bucket-unique-123
   ```

3. **Run development server:**
   ```bash
   python run_dev.py
   ```

4. **Access the API:**
   - **Documentation:** http://localhost:8000/docs
   - **Alternative docs:** http://localhost:8000/redoc
   - **Health check:** http://localhost:8000/health

### Docker Deployment

1. **Build and run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

2. **Or build manually:**
   ```bash
   docker build -t mlops-model-api .
   docker run -p 8000:8000 \
     -e AWS_PROFILE=default \
     -e S3_BUCKET_NAME=mlops-demo-bucket-unique-123 \
     -v ~/.aws:/home/appuser/.aws:ro \
     mlops-model-api
   ```

## 📊 API Endpoints

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information and status |
| `/health` | GET | Health check for monitoring |
| `/metrics` | GET | Performance and usage metrics |
| `/predict` | POST | Single wine quality prediction |
| `/predict/batch` | POST | Batch predictions |
| `/model/reload` | POST | Manually reload model from S3 |

### Prediction Request Format

```json
{
  "features": [7.4, 0.7, 0.0, 1.9, 0.076, 11.0, 34.0, 0.9978, 3.51, 0.56, 9.4]
}
```

Or using named features:
```json
{
  "wine_features": {
    "fixed_acidity": 7.4,
    "volatile_acidity": 0.7,
    "citric_acid": 0.0,
    "residual_sugar": 1.9,
    "chlorides": 0.076,
    "free_sulfur_dioxide": 11.0,
    "total_sulfur_dioxide": 34.0,
    "density": 0.9978,
    "ph": 3.51,
    "sulphates": 0.56,
    "alcohol": 9.4
  }
}
```

### Response Format

```json
{
  "prediction": 6,
  "confidence": 0.87,
  "model_version": "1.0",
  "processing_time_ms": 45.2,
  "features_processed": 11
}
```

## 🧪 Testing

### Automated Testing

Run the comprehensive test suite:
```bash
python test_api.py
```

### Manual Testing

1. **Health check:**
   ```bash
   curl http://localhost:8000/health
   ```

2. **Single prediction:**
   ```bash
   curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{"features": [7.4, 0.7, 0.0, 1.9, 0.076, 11.0, 34.0, 0.9978, 3.51, 0.56, 9.4]}'
   ```

3. **Batch prediction:**
   ```bash
   curl -X POST "http://localhost:8000/predict/batch" \
     -H "Content-Type: application/json" \
     -d '{"features_list": [[7.4, 0.7, 0.0, 1.9, 0.076, 11.0, 34.0, 0.9978, 3.51, 0.56, 9.4]]}'
   ```

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `API_TITLE` | MLOps Model API | API title in documentation |
| `API_VERSION` | 1.0.0 | API version |
| `LOG_LEVEL` | INFO | Logging level |
| `AWS_PROFILE` | default | AWS credentials profile |
| `AWS_DEFAULT_REGION` | us-east-1 | AWS region |
| `S3_BUCKET_NAME` | mlops-demo-bucket-unique-123 | S3 bucket for models |
| `MODEL_KEY` | models/latest/wine_quality_model.joblib | S3 key for model file |
| `MODEL_CACHE_TTL` | 3600 | Model cache time-to-live (seconds) |

### Docker Configuration

The Docker setup includes:
- **Multi-stage build** for optimized image size
- **Non-root user** for security
- **Health checks** for container monitoring
- **Volume mounts** for AWS credentials and model cache
- **Environment configuration** for different deployment scenarios

## 📈 Monitoring

### Health Checks

The `/health` endpoint provides comprehensive system status:
- Model loading status
- S3 connectivity
- Response time metrics
- Service availability

### Metrics

The `/metrics` endpoint tracks:
- Total predictions made
- Success/failure rates
- Average response times
- Model reload events
- System uptime

### Logging

Structured logging includes:
- Request processing times
- Prediction results
- Error details
- Model loading events

## 🔧 Development

### Adding New Features

1. **New endpoints:** Add to `app/main.py`
2. **Request/response models:** Update `app/models/prediction.py`
3. **Business logic:** Extend `app/services/model_service.py`
4. **Configuration:** Modify `app/utils/config.py`

### Code Quality

- **Type hints:** All functions include type annotations
- **Documentation:** Comprehensive docstrings
- **Error handling:** Robust exception management
- **Validation:** Pydantic models for data validation

## 🚢 Production Deployment

### AWS ECS/Fargate

1. Push image to ECR
2. Create ECS task definition
3. Configure load balancer
4. Set up auto-scaling

### Kubernetes

1. Create deployment manifests
2. Configure ingress
3. Set up monitoring
4. Configure horizontal pod autoscaling

### Monitoring Integration

- **Prometheus:** Metrics endpoint compatible
- **Grafana:** Dashboard templates available
- **CloudWatch:** AWS native monitoring
- **DataDog:** APM integration ready

## 🔐 Security

- **Non-root containers** for security
- **Input validation** via Pydantic
- **Error handling** without sensitive data exposure
- **AWS IAM** integration for S3 access
- **CORS configuration** for controlled access

## 🤝 Contributing

1. Follow the established code structure
2. Add tests for new functionality
3. Update documentation
4. Use type hints and docstrings
5. Test with Docker before submitting

## 📝 License

This project is part of the MLOps portfolio demonstration and follows best practices for production ML model serving.

---

**Next Steps:**
- [ ] Add model A/B testing endpoints
- [ ] Implement model performance monitoring
- [ ] Add prediction explanability (SHAP)
- [ ] Set up CI/CD pipeline
- [ ] Add rate limiting and authentication
# Test CI/CD
