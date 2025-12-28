#!/bin/bash
set -e

echo "🚀 MLOps Cloud Deployment Script"
echo "=================================="

# Configuration
AWS_REGION="us-east-1"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPO_NAME="mlops-demo-model-api"
IMAGE_TAG="${1:-latest}"

echo "📋 Configuration:"
echo "  AWS Region: $AWS_REGION"
echo "  AWS Account: $AWS_ACCOUNT_ID"
echo "  Image Tag: $IMAGE_TAG"
echo ""

# Step 1: Initialize Terraform
echo "1️⃣  Initializing Terraform..."
cd terraform
terraform init
echo "✅ Terraform initialized"
echo ""

# Step 2: Plan infrastructure
echo "2️⃣  Planning infrastructure changes..."
terraform plan -out=tfplan
echo "✅ Plan created"
echo ""

# Step 3: Apply infrastructure
read -p "Apply infrastructure changes? (yes/no): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo "❌ Deployment cancelled"
    exit 0
fi

echo "3️⃣  Applying infrastructure..."
terraform apply tfplan
echo "✅ Infrastructure deployed"
echo ""

# Get ECR repository URL from Terraform output
ECR_REPO_URL=$(terraform output -raw ecr_repository_url)
echo "📦 ECR Repository: $ECR_REPO_URL"
echo ""

# Step 4: Build and push Docker image
echo "4️⃣  Building Docker image..."
cd ../../model-api
docker build -t $ECR_REPO_NAME:$IMAGE_TAG .
echo "✅ Image built"
echo ""

echo "5️⃣  Authenticating with ECR..."
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin $ECR_REPO_URL
echo "✅ ECR authenticated"
echo ""

echo "6️⃣  Tagging and pushing image..."
docker tag $ECR_REPO_NAME:$IMAGE_TAG $ECR_REPO_URL:$IMAGE_TAG
docker push $ECR_REPO_URL:$IMAGE_TAG
echo "✅ Image pushed to ECR"
echo ""

# Step 5: Update ECS service
echo "7️⃣  Updating ECS service..."
cd ../infrastructure/terraform
ECS_CLUSTER=$(terraform output -raw ecs_cluster_name)
ECS_SERVICE=$(terraform output -raw ecs_service_name)

aws ecs update-service \
    --cluster $ECS_CLUSTER \
    --service $ECS_SERVICE \
    --force-new-deployment \
    --region $AWS_REGION

echo "✅ ECS service updated"
echo ""

# Display deployment info
echo "🎉 Deployment Complete!"
echo "======================="
ALB_URL=$(terraform output -raw alb_url)
echo "Model API URL: $ALB_URL"
echo ""
echo "Test the API:"
echo "  curl $ALB_URL/health"
echo ""
echo "View logs:"
echo "  aws logs tail $(terraform output -raw cloudwatch_log_group) --follow"
