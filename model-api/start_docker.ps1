# PowerShell startup script for the FastAPI Model API (Docker)

Write-Host "🍷 MLOps Wine Quality Model API - Docker Startup" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green

# Check if Docker is running
try {
    docker info | Out-Null
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running. Please start Docker and try again." -ForegroundColor Red
    exit 1
}

# Check if docker-compose.yml exists
if (-not (Test-Path "docker-compose.yml")) {
    Write-Host "❌ docker-compose.yml not found in current directory" -ForegroundColor Red
    exit 1
}

Write-Host "✅ docker-compose.yml found" -ForegroundColor Green

# Check environment variables
Write-Host "🔍 Checking environment configuration..." -ForegroundColor Yellow
Write-Host "  AWS_PROFILE: $($env:AWS_PROFILE ?? 'default')" -ForegroundColor Gray
Write-Host "  AWS_DEFAULT_REGION: $($env:AWS_DEFAULT_REGION ?? 'us-east-1')" -ForegroundColor Gray
Write-Host "  S3_BUCKET_NAME: $($env:S3_BUCKET_NAME ?? 'mlops-demo-bucket-unique-123')" -ForegroundColor Gray

# Build and start the container
Write-Host "🚀 Building and starting the API container..." -ForegroundColor Blue
docker-compose up --build

Write-Host "🏁 Startup complete!" -ForegroundColor Green
