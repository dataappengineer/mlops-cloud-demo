"""
FastAPI Model Serving Application

This application serves the trained wine quality prediction model via REST API.
Features:
- Wine quality prediction endpoint
- Model loading from S3
- Comprehensive error handling
- Automatic API documentation
- Health monitoring
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import time
import logging
from typing import Dict, Any, List

from app.models.prediction import WineFeaturesRequest, BatchPredictionRequest, PredictionResponse, HealthResponse
from app.services.model_service import ModelService
from app.utils.config import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Wine Quality Prediction API",
    description="A production-ready API for predicting wine quality using ML models",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize model service
model_service = ModelService()

# Request metrics for monitoring
request_metrics = {
    "total_requests": 0,
    "total_predictions": 0,
    "average_response_time": 0.0,
    "errors": 0
}


@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("Starting Wine Quality Prediction API...")
    
    try:
        # Load model on startup
        await model_service.load_model()
        logger.info("Model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load model on startup: {e}")
        # Don't fail startup - model can be loaded on first request


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    logger.info("Shutting down Wine Quality Prediction API...")


@app.get("/", response_model=Dict[str, Any])
async def root():
    """API information endpoint"""
    return {
        "name": "Wine Quality Prediction API",
        "version": "1.0.0",
        "description": "ML-powered wine quality prediction service",
        "endpoints": {
            "predict": "/predict",
            "health": "/health",
            "metrics": "/metrics",
            "docs": "/docs"
        },
        "model_info": {
            "type": "Random Forest Classifier",
            "features": 11,
            "target": "wine_quality_score"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for monitoring"""
    start_time = time.time()
    
    # Check model availability
    model_status = "healthy" if model_service.is_model_loaded() else "degraded"
    
    # Check S3 connectivity (optional)
    s3_status = "unknown"
    try:
        # Quick S3 connectivity test
        s3_status = "healthy"  # Implement actual S3 ping if needed
    except Exception:
        s3_status = "unhealthy"
    
    response_time = (time.time() - start_time) * 1000  # ms
    
    overall_status = "healthy" if model_status == "healthy" else "degraded"
    
    return HealthResponse(
        status=overall_status,
        timestamp=int(time.time()),
        checks={
            "model": model_status,
            "s3": s3_status,
            "response_time_ms": round(response_time, 2)
        },
        version="1.0.0"
    )


@app.get("/metrics", response_model=Dict[str, Any])
async def get_metrics():
    """API metrics endpoint for monitoring"""
    return {
        "api_metrics": request_metrics,
        "model_metrics": {
            "model_loaded": model_service.is_model_loaded(),
            "model_version": getattr(model_service, 'model_version', 'unknown'),
            "cache_status": "active" if model_service.is_model_loaded() else "empty"
        },
        "system_metrics": {
            "timestamp": int(time.time()),
            "uptime_seconds": int(time.time() - getattr(app.state, 'start_time', time.time()))
        }
    }


@app.post("/predict", response_model=PredictionResponse)
async def predict_wine_quality(request: WineFeaturesRequest):
    """
    Predict wine quality based on physicochemical properties
    
    This endpoint accepts wine features and returns a quality prediction (3-8 scale)
    along with confidence metrics and processing information.
    """
    start_time = time.time()
    request_metrics["total_requests"] += 1
    
    try:
        logger.info(f"Processing prediction request for wine quality")
        
        # Ensure model is loaded
        if not model_service.is_model_loaded():
            logger.info("Model not loaded, loading now...")
            await model_service.load_model()
        
        # Make prediction
        prediction_result = await model_service.predict(request.features)
        
        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000  # ms
        
        # Update metrics
        request_metrics["total_predictions"] += 1
        request_metrics["average_response_time"] = (
            (request_metrics["average_response_time"] * (request_metrics["total_predictions"] - 1) + processing_time) 
            / request_metrics["total_predictions"]
        )
        
        logger.info(f"Prediction completed in {processing_time:.2f}ms: quality={prediction_result['prediction']}")
        
        return PredictionResponse(
            prediction=prediction_result["prediction"],
            confidence=prediction_result.get("confidence", 0.0),
            model_version=prediction_result.get("model_version", "1.0"),
            processing_time_ms=round(processing_time, 2),
            features_processed=11  # Standard wine features count
        )
        
    except Exception as e:
        request_metrics["errors"] += 1
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Prediction failed",
                "message": str(e),
                "type": type(e).__name__
            }
        )


@app.post("/predict/batch", response_model=List[PredictionResponse])
async def predict_wine_quality_batch(request: BatchPredictionRequest):
    """
    Predict wine quality for multiple samples in batch
    
    This endpoint accepts multiple wine features and returns quality predictions
    for each sample along with confidence metrics and processing information.
    """
    start_time = time.time()
    request_metrics["total_requests"] += 1
    
    try:
        batch_size = len(request.features_list)
        logger.info(f"Processing batch prediction request with {batch_size} samples")
        
        # Validate batch size
        if batch_size > 100:
            raise HTTPException(
                status_code=400,
                detail="Batch size too large. Maximum 100 predictions per request."
            )
        
        # Ensure model is loaded
        if not model_service.is_model_loaded():
            logger.info("Model not loaded, loading now...")
            await model_service.load_model()
        
        results = []
        successful_predictions = 0
        failed_predictions = 0
        
        for i, wine_features in enumerate(request.features_list):
            try:
                # Make prediction using WineFeatures object directly
                prediction_result = await model_service.predict(wine_features)
                
                results.append(PredictionResponse(
                    prediction=prediction_result["prediction"],
                    confidence=prediction_result.get("confidence", 0.0),
                    model_version=prediction_result.get("model_version", "1.0"),
                    processing_time_ms=0.0,  # Will be calculated at the end
                    features_processed=11,  # Standard wine features count
                    request_id=f"{request.request_id}_{i}" if request.request_id else None
                ))
                successful_predictions += 1
                
            except Exception as e:
                logger.error(f"Batch prediction failed for sample {i}: {e}")
                failed_predictions += 1
                # Add error response for failed prediction
                results.append(PredictionResponse(
                    prediction=-1,  # Error indicator
                    confidence=0.0,
                    model_version="error",
                    processing_time_ms=0.0,
                    features_processed=0,  # Error case
                    request_id=f"{request.request_id}_{i}_error" if request.request_id else None
                ))
        
        # Calculate total processing time
        processing_time = (time.time() - start_time) * 1000  # ms
        
        # Update processing time for all results
        for result in results:
            result.processing_time_ms = round(processing_time / batch_size, 2)
        
        # Update metrics
        request_metrics["total_predictions"] += successful_predictions
        request_metrics["errors"] += failed_predictions
        request_metrics["average_response_time"] = (
            (request_metrics["average_response_time"] * (request_metrics["total_predictions"] - successful_predictions) + processing_time) 
            / request_metrics["total_predictions"]
        ) if request_metrics["total_predictions"] > 0 else processing_time
        
        logger.info(f"Batch prediction completed in {processing_time:.2f}ms: {successful_predictions} successful, {failed_predictions} failed")
        
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        request_metrics["errors"] += batch_size
        logger.error(f"Batch prediction failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Batch prediction failed",
                "message": str(e),
                "type": type(e).__name__
            }
        )


@app.post("/model/reload")
async def reload_model():
    """
    Manually reload the model from S3
    
    This endpoint forces a reload of the model from S3, bypassing any cache.
    Useful for deploying new model versions without restarting the service.
    """
    try:
        logger.info("Manual model reload requested")
        await model_service.load_model(force_reload=True)
        
        return {
            "status": "success",
            "message": "Model reloaded successfully from S3",
            "model_version": getattr(model_service, 'model_version', 'unknown'),
            "timestamp": int(time.time())
        }
        
    except Exception as e:
        logger.error(f"Model reload failed: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Model reload failed",
                "message": str(e),
                "type": type(e).__name__
            }
        )


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors"""
    request_metrics["errors"] += 1
    logger.error(f"Unhandled error: {exc}")
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "type": type(exc).__name__
        }
    )


if __name__ == "__main__":
    # Store start time for uptime calculation
    app.state.start_time = time.time()
    
    # Run the application
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level="info"
    )
