# MLOps Cloud Demo

> **Portfolio Project**: Production-grade MLOps pipeline demonstrating data engineering, ML orchestration, and cloud deployment best practices.

## 🏗️ Project Structure

```
mlops-cloud-demo/
├── data-pipeline/         # Airflow-based data ingestion & processing
├── model-api/             # FastAPI model serving endpoint  
├── infrastructure/        # Terraform IaC for AWS resources
└── docs/                  # Architecture & setup documentation
```

### Components

- **[data-pipeline/](./data-pipeline/)**: Apache Airflow DAGs for data ingestion, cleaning, validation, and S3 upload. Self-contained with Docker Compose.

- **[model-api/](./model-api/)**: FastAPI REST API for model predictions. Dockerized with health checks and proper configuration management.

- **[infrastructure/](./infrastructure/)**: Terraform configurations for AWS resources (S3, IAM, etc.). Isolated from application code.

- **[docs/](./docs/)**: Comprehensive documentation including AWS setup, learning journey, and technical notes.

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- AWS Account with CLI configured
- Python 3.9+

### Data Pipeline
```bash
cd data-pipeline
cp .env.example .env  # Add your AWS credentials
docker build -t mlops-airflow:custom-2.8.1 .
docker-compose up -d
# Access Airflow UI: http://localhost:8080 (admin/admin)
```

### Model API
```bash
cd model-api
docker-compose up -d
# Access API docs: http://localhost:8000/docs
```

### Infrastructure
```bash
cd infrastructure/terraform
cp ../.env.example ../.env  # Configure AWS credentials
terraform init
terraform plan
terraform apply
```

## 📚 Documentation

- **[Learning Journey](./docs/learning-journey.md)**: Iterative development process, challenges, and solutions
- **[AWS Setup](./docs/aws-setup/)**: Detailed AWS configuration and security best practices
- **[Technical Notes](./docs/technical-notes/)**: Deep dives into specific implementation decisions

## 🎯 Project Goals

- ✅ Automate end-to-end ML workflow (data → training → deployment)
- ✅ Production-grade code with proper error handling and logging
- ✅ Cloud-native architecture with AWS integration
- ✅ Self-contained, independently deployable components
- 🚧 Model monitoring and observability (in progress)
- 🚧 CI/CD pipeline automation (planned)

## 💡 Key Learnings

This project demonstrates:
- **Infrastructure as Code** with Terraform
- **Containerization** with Docker & Docker Compose
- **Workflow Orchestration** with Apache Airflow
- **API Development** with FastAPI
- **Cloud Integration** with AWS (S3, IAM)
- **Monorepo Best Practices** for multi-component systems

See [learning-journey.md](./docs/learning-journey.md) for detailed technical stories and problem-solving approaches.

---

**Status**: Active Development  
**Last Updated**: December 27, 2025  
**Author**: Giovanni Brucoli ([dataappengineer](https://github.com/dataappengineer))
