# MLOps Cloud Infrastructure (Terraform)

Infrastructure as Code for deploying the MLOps model serving API to AWS using ECS Fargate.

## 🏗️ Architecture

```
Internet → ALB → ECS Fargate (Model API) → S3 (Model Artifacts)
```

### Components
- **VPC**: Custom VPC with public/private subnets across 2 AZs
- **ECS Fargate**: Serverless container orchestration (Free Tier eligible)
- **ALB**: Application Load Balancer
- **ECR**: Docker image registry
- **S3**: Model artifact storage (existing bucket)
- **CloudWatch**: Logging and monitoring

## 💰 Cost Optimization
- ECS Fargate: 750 hours/month free (1 task)
- NAT Gateway: **Disabled by default** (saves $32/month)
- All resources configured for Free Tier

## 🚀 Quick Start

### 1. Configure Variables
```bash
cp terraform.tfvars.example terraform.tfvars
```

### 2. Deploy
```bash
terraform init
terraform plan
terraform apply
```

### 3. Build & Push Image
```bash
ECR_REPO=$(terraform output -raw ecr_repository_url)
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $ECR_REPO
cd ../../model-api
docker build -t model-api:latest .
docker tag model-api:latest $ECR_REPO:latest
docker push $ECR_REPO:latest
```

### 4. Update ECS
```bash
aws ecs update-service \\
  --cluster $(terraform output -raw ecs_cluster_name) \\
  --service $(terraform output -raw ecs_service_name) \\
  --force-new-deployment
```

### 5. Test API
```bash
curl $(terraform output -raw alb_url)/health
```

## 🛠️ Automated Deployment
```bash
cd ../infrastructure
./deploy.sh
```

## 📊 Monitoring
```bash
# View logs
aws logs tail $(terraform output -raw cloudwatch_log_group) --follow

# Check service status
aws ecs describe-services \\
  --cluster $(terraform output -raw ecs_cluster_name) \\
  --services $(terraform output -raw ecs_service_name)
```

## 🗑️ Teardown
```bash
./destroy.sh
# or
terraform destroy
```

## 📁 Files
- `main.tf` - Provider configuration
- `variables.tf` - Input variables
- `outputs.tf` - Output values
- `vpc.tf` - VPC and networking
- `ecs.tf` - ECS cluster/service
- `alb.tf` - Load balancer
- `iam.tf` - IAM roles
- `ecr.tf` - Container registry

## 🔒 Security
- IAM least privilege access
- Security groups with restricted rules
- Private subnets for ECS tasks
- ALB as single public entry point

## 📚 Resources
- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/)
- [AWS Free Tier](https://aws.amazon.com/free/)
