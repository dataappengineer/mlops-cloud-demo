"""
Pydantic models for API request/response validation

These models define the structure and validation rules for:
- Wine features input
- Prediction responses  
- Health check responses
- Error responses
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class WineFeatures(BaseModel):
    """
    Wine physicochemical properties for quality prediction
    
    All features are based on the UCI Wine Quality dataset:
    - Features represent measurable wine properties
    - Ranges are based on real-world wine analysis data
    - Validation ensures realistic input values
    """
    
    fixed_acidity: float = Field(
        ..., 
        ge=4.0, 
        le=16.0,
        description="Fixed acidity (tartaric acid - g/dm³)"
    )
    
    volatile_acidity: float = Field(
        ..., 
        ge=0.1, 
        le=2.0,
        description="Volatile acidity (acetic acid - g/dm³)"
    )
    
    citric_acid: float = Field(
        ..., 
        ge=0.0, 
        le=1.5,
        description="Citric acid (g/dm³)"
    )
    
    residual_sugar: float = Field(
        ..., 
        ge=0.5, 
        le=20.0,
        description="Residual sugar (g/dm³)"
    )
    
    chlorides: float = Field(
        ..., 
        ge=0.01, 
        le=0.7,
        description="Chlorides (sodium chloride - g/dm³)"
    )
    
    free_sulfur_dioxide: float = Field(
        ..., 
        ge=1.0, 
        le=100.0,
        description="Free sulfur dioxide (mg/dm³)"
    )
    
    total_sulfur_dioxide: float = Field(
        ..., 
        ge=5.0, 
        le=300.0,
        description="Total sulfur dioxide (mg/dm³)"
    )
    
    density: float = Field(
        ..., 
        ge=0.99, 
        le=1.01,
        description="Density (g/cm³)"
    )
    
    ph: float = Field(
        ..., 
        ge=2.5, 
        le=4.5,
        description="pH level"
    )
    
    sulphates: float = Field(
        ..., 
        ge=0.3, 
        le=2.0,
        description="Sulphates (potassium sulphate - g/dm³)"
    )
    
    alcohol: float = Field(
        ..., 
        ge=8.0, 
        le=15.0,
        description="Alcohol content (% by volume)"
    )
    
    @validator('free_sulfur_dioxide', 'total_sulfur_dioxide')
    def validate_sulfur_dioxide_relationship(cls, v, values):
        """Ensure free sulfur dioxide is not greater than total sulfur dioxide"""
        if 'total_sulfur_dioxide' in values and 'free_sulfur_dioxide' in values:
            if values.get('free_sulfur_dioxide', 0) > v:
                raise ValueError("Free sulfur dioxide cannot exceed total sulfur dioxide")
        return v
    
    def to_feature_vector(self) -> list:
        """Convert to ordered feature vector for model prediction"""
        return [
            self.fixed_acidity,
            self.volatile_acidity,
            self.citric_acid,
            self.residual_sugar,
            self.chlorides,
            self.free_sulfur_dioxide,
            self.total_sulfur_dioxide,
            self.density,
            self.ph,
            self.sulphates,
            self.alcohol
        ]
    
    class Config:
        schema_extra = {
            "example": {
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


class WineFeaturesRequest(BaseModel):
    """Request model for wine quality prediction"""
    
    features: WineFeatures = Field(
        ...,
        description="Wine physicochemical properties for quality prediction"
    )
    
    request_id: Optional[str] = Field(
        None,
        description="Optional request identifier for tracking"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "features": {
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
                },
                "request_id": "req_123456789"
            }
        }


class BatchPredictionRequest(BaseModel):
    """Request model for batch wine quality predictions"""
    
    features_list: List[WineFeatures] = Field(
        ...,
        min_items=1,
        max_items=100,
        description="List of wine features for batch prediction (max 100)"
    )
    
    request_id: Optional[str] = Field(
        None,
        description="Optional request identifier for tracking"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "features_list": [
                    {
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
                    },
                    {
                        "fixed_acidity": 7.8,
                        "volatile_acidity": 0.88,
                        "citric_acid": 0.0,
                        "residual_sugar": 2.6,
                        "chlorides": 0.098,
                        "free_sulfur_dioxide": 25.0,
                        "total_sulfur_dioxide": 67.0,
                        "density": 0.9968,
                        "ph": 3.2,
                        "sulphates": 0.68,
                        "alcohol": 9.8
                    }
                ],
                "request_id": "batch_req_123456789"
            }
        }


class PredictionResponse(BaseModel):
    """Response model for wine quality prediction"""
    
    prediction: int = Field(
        ...,
        ge=-1,  # Allow -1 for error cases
        le=8,
        description="Predicted wine quality score (3-8 scale), -1 for errors"
    )
    
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Model confidence score (0.0-1.0)"
    )
    
    model_version: str = Field(
        ...,
        description="Version of the model used for prediction"
    )
    
    processing_time_ms: float = Field(
        ...,
        description="Request processing time in milliseconds"
    )
    
    features_processed: int = Field(
        ...,
        description="Number of features processed"
    )
    
    request_id: Optional[str] = Field(
        None,
        description="Request identifier if provided"
    )
    
    error: Optional[str] = Field(
        None,
        description="Error message if prediction failed"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "prediction": 5,
                "confidence": 0.87,
                "model_version": "1.0",
                "processing_time_ms": 23.45,
                "features_processed": 11,
                "request_id": "req_123456789"
            }
        }


class HealthResponse(BaseModel):
    """Response model for health check endpoint"""
    
    status: str = Field(
        ...,
        description="Overall service status (healthy/degraded/unhealthy)"
    )
    
    timestamp: int = Field(
        ...,
        description="Unix timestamp of health check"
    )
    
    checks: Dict[str, Any] = Field(
        ...,
        description="Individual component health checks"
    )
    
    version: str = Field(
        ...,
        description="API version"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": 1692835200,
                "checks": {
                    "model": "healthy",
                    "s3": "healthy",
                    "response_time_ms": 15.23
                },
                "version": "1.0.0"
            }
        }


class ErrorResponse(BaseModel):
    """Response model for error cases"""
    
    error: str = Field(
        ...,
        description="Error category"
    )
    
    message: str = Field(
        ...,
        description="Detailed error message"
    )
    
    type: str = Field(
        ...,
        description="Error type/class"
    )
    
    request_id: Optional[str] = Field(
        None,
        description="Request identifier if provided"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "error": "Validation Error",
                "message": "Invalid feature values provided",
                "type": "ValidationError",
                "request_id": "req_123456789"
            }
        }
