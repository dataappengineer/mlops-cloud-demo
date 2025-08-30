"""
Model Service for loading and serving ML models

This service handles:
- Loading trained models from S3
- Local model caching
- Model prediction logic
- Error handling and validation
"""

import os
import time
import joblib
import logging
import asyncio
from typing import Optional, Dict, Any, List
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
import numpy as np
from sklearn.ensemble import RandomForestClassifier

from app.utils.config import get_settings, get_aws_config, create_model_cache_dir
from app.models.prediction import WineFeatures

logger = logging.getLogger(__name__)


class ModelService:
    """Service for managing ML model lifecycle and predictions"""
    
    def __init__(self):
        self.settings = get_settings()
        self.model: Optional[RandomForestClassifier] = None
        self.model_version: str = "1.0"
        self.model_loaded_at: Optional[float] = None
        self.s3_client = None
        self.cache_dir = create_model_cache_dir()
        
        # Initialize S3 client
        self._init_s3_client()
    
    def _init_s3_client(self):
        """Initialize S3 client with configuration"""
        try:
            aws_config = get_aws_config()
            self.s3_client = boto3.client('s3', **aws_config)
            logger.info("S3 client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize S3 client: {e}")
            self.s3_client = None
    
    def _get_cached_model_path(self) -> str:
        """Get local path for cached model"""
        return os.path.join(self.cache_dir, self.settings.model_path)
    
    def _is_cache_valid(self) -> bool:
        """Check if cached model is still valid based on TTL"""
        cached_path = self._get_cached_model_path()
        
        if not os.path.exists(cached_path):
            return False
        
        # Check file age against TTL
        file_age = time.time() - os.path.getmtime(cached_path)
        return file_age < self.settings.model_cache_ttl
    
    async def _download_model_from_s3(self) -> str:
        """Download model from S3 to local cache"""
        if not self.s3_client:
            raise RuntimeError("S3 client not initialized")
        
        cached_path = self._get_cached_model_path()
        
        try:
            logger.info(f"Downloading model from S3: s3://{self.settings.s3_bucket_name}/{self.settings.model_path}")
            
            # Download in a thread to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self.s3_client.download_file,
                self.settings.s3_bucket_name,
                self.settings.model_path,
                cached_path
            )
            
            logger.info(f"Model downloaded successfully to {cached_path}")
            return cached_path
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'NoSuchKey':
                raise FileNotFoundError(f"Model not found in S3: {self.settings.model_path}")
            elif error_code == 'NoSuchBucket':
                raise FileNotFoundError(f"S3 bucket not found: {self.settings.s3_bucket_name}")
            else:
                raise RuntimeError(f"S3 error: {e}")
        
        except NoCredentialsError:
            raise RuntimeError("AWS credentials not found. Please configure AWS credentials.")
        
        except Exception as e:
            raise RuntimeError(f"Failed to download model from S3: {e}")
    
    def _load_model_from_file(self, model_path: str) -> RandomForestClassifier:
        """Load model from local file"""
        try:
            logger.info(f"Loading model from {model_path}")
            model = joblib.load(model_path)
            
            # Validate model type
            if not isinstance(model, RandomForestClassifier):
                raise ValueError(f"Expected RandomForestClassifier, got {type(model)}")
            
            # Validate model has required attributes
            if not hasattr(model, 'predict') or not hasattr(model, 'predict_proba'):
                raise ValueError("Model missing required methods")
            
            logger.info("Model loaded and validated successfully")
            return model
            
        except Exception as e:
            raise RuntimeError(f"Failed to load model from file: {e}")
    
    async def load_model(self, force_reload: bool = False) -> bool:
        """Load model with caching and S3 fallback"""
        try:
            cached_path = self._get_cached_model_path()
            
            # Try to use cached model if valid and not forcing reload
            if not force_reload and self._is_cache_valid():
                logger.info("Using cached model")
                self.model = self._load_model_from_file(cached_path)
            else:
                # Download fresh model from S3
                logger.info("Cache invalid or missing, downloading from S3")
                downloaded_path = await self._download_model_from_s3()
                self.model = self._load_model_from_file(downloaded_path)
            
            self.model_loaded_at = time.time()
            logger.info(f"Model loaded successfully at {self.model_loaded_at}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self.model = None
            self.model_loaded_at = None
            raise
    
    def is_model_loaded(self) -> bool:
        """Check if model is currently loaded"""
        return self.model is not None
    
    def _prepare_features(self, features: WineFeatures) -> np.ndarray:
        """Prepare features for model prediction"""
        feature_vector = features.to_feature_vector()
        
        # Validate feature count
        if len(feature_vector) != 11:
            raise ValueError(f"Expected 11 features, got {len(feature_vector)}")
        
        # Convert to numpy array and reshape for single prediction
        return np.array(feature_vector).reshape(1, -1)
    
    def _calculate_confidence(self, probabilities: np.ndarray) -> float:
        """Calculate prediction confidence from class probabilities"""
        # Use the maximum probability as confidence
        max_prob = np.max(probabilities)
        return float(max_prob)
    
    async def predict(self, features: WineFeatures) -> Dict[str, Any]:
        """Make wine quality prediction"""
        if not self.is_model_loaded():
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        try:
            # Prepare features
            X = self._prepare_features(features)
            
            # Make prediction
            prediction = self.model.predict(X)[0]
            
            # Get prediction probabilities for confidence calculation
            probabilities = self.model.predict_proba(X)[0]
            confidence = self._calculate_confidence(probabilities)
            
            # Ensure prediction is within valid range (3-8)
            prediction = int(np.clip(prediction, 3, 8))
            
            result = {
                "prediction": prediction,
                "confidence": round(confidence, 4),
                "model_version": self.model_version,
                "probabilities": probabilities.tolist(),  # For debugging
                "feature_count": len(features.to_feature_vector())
            }
            
            logger.debug(f"Prediction result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            raise RuntimeError(f"Prediction failed: {e}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        if not self.is_model_loaded():
            return {"status": "not_loaded"}
        
        try:
            return {
                "status": "loaded",
                "model_type": type(self.model).__name__,
                "n_estimators": getattr(self.model, 'n_estimators', 'unknown'),
                "n_features": getattr(self.model, 'n_features_in_', 'unknown'),
                "classes": getattr(self.model, 'classes_', []).tolist(),
                "loaded_at": self.model_loaded_at,
                "version": self.model_version,
                "cache_path": self._get_cached_model_path()
            }
        except Exception as e:
            logger.error(f"Failed to get model info: {e}")
            return {"status": "error", "error": str(e)}
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on model service"""
        health = {
            "model_loaded": self.is_model_loaded(),
            "s3_client": self.s3_client is not None,
            "cache_dir_exists": os.path.exists(self.cache_dir),
            "cache_valid": self._is_cache_valid() if self.is_model_loaded() else False
        }
        
        # Test S3 connectivity
        if self.s3_client:
            try:
                # Simple S3 operation to test connectivity
                await asyncio.get_event_loop().run_in_executor(
                    None,
                    self.s3_client.head_bucket,
                    Bucket=self.settings.s3_bucket_name
                )
                health["s3_connectivity"] = True
            except Exception as e:
                health["s3_connectivity"] = False
                health["s3_error"] = str(e)
        else:
            health["s3_connectivity"] = False
        
        return health
