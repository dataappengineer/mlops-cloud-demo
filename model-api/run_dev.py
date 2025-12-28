#!/usr/bin/env python3
"""
Local development server for the FastAPI model service.

This script provides a convenient way to run the API locally
with development settings and environment configuration.
"""

import os
import sys
import uvicorn
import subprocess
from pathlib import Path

# Add the app directory to the Python path
app_dir = Path(__file__).parent / "app"
sys.path.insert(0, str(app_dir))

def check_environment():
    """Check if the environment is properly configured"""
    print("🔍 Checking environment configuration...")
    
    # Check AWS credentials
    aws_profile = os.getenv("AWS_PROFILE", "default")
    aws_region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
    s3_bucket = os.getenv("S3_BUCKET_NAME", "mlops-demo-bucket-unique-123")
    
    print(f"  AWS Profile: {aws_profile}")
    print(f"  AWS Region: {aws_region}")
    print(f"  S3 Bucket: {s3_bucket}")
    
    # Check if AWS CLI is configured
    try:
        result = subprocess.run(
            ["aws", "sts", "get-caller-identity"], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        if result.returncode == 0:
            print("  ✅ AWS credentials are configured")
        else:
            print("  ⚠️  AWS credentials may not be configured properly")
            print(f"    Error: {result.stderr}")
    except FileNotFoundError:
        print("  ⚠️  AWS CLI not found - install with: pip install awscli")
    except subprocess.TimeoutExpired:
        print("  ⚠️  AWS CLI check timed out")
    except Exception as e:
        print(f"  ⚠️  Error checking AWS configuration: {e}")
    
    print()

def run_server():
    """Run the FastAPI development server"""
    print("🚀 Starting FastAPI Model Service...")
    print("=" * 50)
    
    # Set environment variables for development
    os.environ.setdefault("LOG_LEVEL", "INFO")
    os.environ.setdefault("API_TITLE", "MLOps Model API")
    os.environ.setdefault("API_VERSION", "1.0.0")
    
    # Run the server
    try:
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
            access_log=True,
            app_dir=str(app_dir)
        )
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Server error: {e}")

def main():
    """Main function"""
    print("🍷 MLOps Wine Quality Model API")
    print("=" * 50)
    
    check_environment()
    
    print("📋 Available endpoints after startup:")
    print("  • API Documentation: http://localhost:8000/docs")
    print("  • Alternative Docs: http://localhost:8000/redoc")
    print("  • Health Check: http://localhost:8000/health")
    print("  • Metrics: http://localhost:8000/metrics")
    print("  • Prediction: http://localhost:8000/predict")
    print()
    
    print("🔧 Development notes:")
    print("  • Auto-reload enabled for code changes")
    print("  • Model will be loaded from S3 on first request")
    print("  • Use Ctrl+C to stop the server")
    print()
    
    input("Press Enter to start the server...")
    run_server()

if __name__ == "__main__":
    main()
