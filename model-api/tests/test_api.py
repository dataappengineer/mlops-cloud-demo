"""
Tests for FastAPI model prediction endpoints
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
import os

# Set test environment variables before importing app
os.environ['MODEL_BUCKET'] = 'test-bucket'
os.environ['MODEL_KEY'] = 'test-model.pkl'
os.environ['AWS_REGION'] = 'us-east-1'
os.environ['ENVIRONMENT'] = 'test'

from app.main import app

client = TestClient(app)


@pytest.fixture
def mock_model_service():
    """Mock the model service for prediction tests"""
    with patch('app.main.model_service') as mock:
        # Mock the predict method as an async function
        mock.predict = AsyncMock(return_value={
            "prediction": 5,
            "confidence": 0.98,
            "model_version": "1.0"
        })
        # Mock load_model to avoid startup errors
        mock.load_model = AsyncMock()
        mock.model_loaded = True
        yield mock


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_endpoint_returns_200(self):
        """Health endpoint should return 200 OK"""
        response = client.get("/health")
        assert response.status_code == 200
    
    def test_health_endpoint_returns_json(self):
        """Health endpoint should return JSON"""
        response = client.get("/health")
        assert response.headers["content-type"] == "application/json"
    
    def test_health_endpoint_structure(self):
        """Health endpoint should have correct structure"""
        response = client.get("/health")
        data = response.json()
        
        assert "status" in data
        assert "timestamp" in data
        assert "checks" in data
        assert data["status"] in ["healthy", "unhealthy", "degraded"]


class TestPredictionEndpoint:
    """Test prediction endpoint"""
    
    def test_predict_endpoint_accepts_valid_input(self, mock_model_service):
        """Prediction endpoint should accept valid wine features"""
        payload = {
            "features": {
                "fixed_acidity": 7.4,
                "volatile_acidity": 0.7,
                "citric_acid": 0.0,
                "residual_sugar": 1.9,
                "chlorides": 0.076,
                "free_sulfur_dioxide": 11,
                "total_sulfur_dioxide": 34,
                "density": 0.9978,
                "ph": 3.51,
                "sulphates": 0.56,
                "alcohol": 9.4
            }
        }
        
        response = client.post("/predict", json=payload)
        assert response.status_code == 200
    
    def test_predict_endpoint_returns_prediction(self, mock_model_service):
        """Prediction endpoint should return prediction with correct structure"""
        payload = {
            "features": {
                "fixed_acidity": 7.4,
                "volatile_acidity": 0.7,
                "citric_acid": 0.0,
                "residual_sugar": 1.9,
                "chlorides": 0.076,
                "free_sulfur_dioxide": 11,
                "total_sulfur_dioxide": 34,
                "density": 0.9978,
                "ph": 3.51,
                "sulphates": 0.56,
                "alcohol": 9.4
            }
        }
        
        response = client.post("/predict", json=payload)
        data = response.json()
        
        assert "prediction" in data
        assert "confidence" in data
        assert "model_version" in data
        assert isinstance(data["prediction"], (int, float))
        assert 0 <= data["confidence"] <= 1
    
    def test_predict_endpoint_rejects_invalid_input(self):
        """Prediction endpoint should reject invalid input"""
        payload = {
            "features": {
                "fixed_acidity": "invalid",  # Should be numeric
                "volatile_acidity": 0.7
            }
        }
        
        response = client.post("/predict", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_predict_endpoint_rejects_missing_fields(self):
        """Prediction endpoint should reject incomplete input"""
        payload = {
            "features": {
                "fixed_acidity": 7.4
                # Missing other required fields
            }
        }
        
        response = client.post("/predict", json=payload)
        assert response.status_code == 422


class TestRootEndpoint:
    """Test root endpoint"""
    
    def test_root_endpoint_returns_200(self):
        """Root endpoint should return 200 OK"""
        response = client.get("/")
        assert response.status_code == 200
    
    def test_root_endpoint_returns_welcome_message(self):
        """Root endpoint should return welcome message"""
        response = client.get("/")
        data = response.json()
        
        assert "name" in data
        assert "Wine Quality" in data["name"] or "API" in data["name"]
