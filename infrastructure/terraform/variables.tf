variable "aws_region" {
  description = "AWS region for resource deployment"
  type        = string
  default     = "us-east-1"
}

variable "aws_profile" {
  description = "AWS CLI profile to use"
  type        = string
  default     = "mlops-dev-user"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "mlops-demo"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "s3_bucket_name" {
  description = "Existing S3 bucket for model artifacts"
  type        = string
  default     = "mlops-processed-data-982248023588"
}

variable "model_api_container_port" {
  description = "Port exposed by model API container"
  type        = number
  default     = 8000
}

variable "model_api_cpu" {
  description = "CPU units for model API task (1024 = 1 vCPU)"
  type        = number
  default     = 256  # 0.25 vCPU - Free Tier eligible
}

variable "model_api_memory" {
  description = "Memory for model API task in MB"
  type        = number
  default     = 512  # 0.5 GB - Free Tier eligible
}

variable "model_api_desired_count" {
  description = "Desired number of model API tasks"
  type        = number
  default     = 1
}

variable "enable_nat_gateway" {
  description = "Enable NAT Gateway (costs money, set false for dev)"
  type        = bool
  default     = false
}

variable "tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default = {
    Project     = "MLOps-Cloud-Demo"
    ManagedBy   = "Terraform"
    Environment = "dev"
  }
}