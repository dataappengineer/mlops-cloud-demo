#!/bin/bash
# Docker-based startup script for the FastAPI Model API

echo "🍷 MLOps Wine Quality Model API - Docker Startup"
echo "=================================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

echo "✅ Docker is running"

# Check if docker-compose.yml exists
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ docker-compose.yml not found in current directory"
    exit 1
fi

echo "✅ docker-compose.yml found"

# Check environment variables
echo "🔍 Checking environment configuration..."
echo "  AWS_PROFILE: ${AWS_PROFILE:-default}"
echo "  AWS_DEFAULT_REGION: ${AWS_DEFAULT_REGION:-us-east-1}"
echo "  S3_BUCKET_NAME: ${S3_BUCKET_NAME:-mlops-demo-bucket-unique-123}"

# Build and start the container
echo "🚀 Building and starting the API container..."
docker-compose up --build

echo "🏁 Startup complete!"
