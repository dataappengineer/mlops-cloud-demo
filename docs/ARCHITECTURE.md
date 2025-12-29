# MLOps Cloud Demo - System Architecture

## High-Level Architecture

```mermaid
graph TB
    subgraph "Development"
        Dev[Developer] -->|git push| GH[GitHub]
    end
    
    subgraph "CI/CD - GitHub Actions"
        GH -->|trigger| CI[Build & Test]
        CI -->|docker build| ECR[AWS ECR]
        CI -->|deploy| ECS[ECS Service Update]
    end
    
    subgraph "AWS Cloud Infrastructure"
        subgraph "VPC - us-east-1"
            ALB[Application Load Balancer<br/>Port 80]
            
            subgraph "ECS Fargate Cluster"
                Task1[ECS Task<br/>FastAPI Container<br/>0.25 vCPU, 512MB RAM]
            end
            
            ALB -->|route traffic| Task1
            Task1 -->|load model| S3[S3 Bucket<br/>ml-models/wine-quality-model.pkl]
        end
        
        subgraph "Monitoring"
            Task1 -->|logs| CWL[CloudWatch Logs]
            Task1 -->|metrics| CWM[CloudWatch Metrics<br/>TotalRequests, Errors, Latency]
            CWM --> Dashboard[CloudWatch Dashboard<br/>MLOps-Model-API]
        end
    end
    
    subgraph "Users"
        Client[API Clients] -->|HTTP requests| ALB
        Status[Status Page<br/>GitHub Pages] -.->|monitor| Dashboard
    end
    
    subgraph "Data Pipeline - Airflow"
        Airflow[Apache Airflow DAGs] -->|upload| S3
        Airflow -->|train| Model[scikit-learn Model]
        Model -->|save| S3
    end
    
    style Task1 fill:#4CAF50
    style Dashboard fill:#FF9800
    style S3 fill:#2196F3
    style ALB fill:#9C27B0
```

## Component Details

### 1. CI/CD Pipeline
- **GitHub Actions**: Automated testing, Docker build, and deployment
- **Workflow**: Test → Build → Push to ECR → Deploy to ECS
- **Trigger**: Push to main branch

### 2. Cloud Infrastructure (AWS)
- **ECS Fargate**: Serverless container orchestration
- **Application Load Balancer**: HTTP traffic routing
- **VPC**: Isolated network with public/private subnets
- **ECR**: Docker image registry
- **S3**: Model artifact storage

### 3. API Service
- **FastAPI**: High-performance Python web framework
- **Endpoints**: `/health`, `/predict`, `/metrics`, `/docs`
- **Model**: scikit-learn Random Forest loaded from S3
- **Container**: 0.25 vCPU, 512MB RAM (AWS Free Tier eligible)

### 4. Monitoring & Observability
- **CloudWatch Logs**: Application logs from ECS tasks
- **CloudWatch Metrics**: Custom metrics (requests, errors, latency)
- **CloudWatch Dashboard**: Real-time visualization
- **Status Page**: Public GitHub Pages dashboard

### 5. Data Pipeline
- **Apache Airflow**: Orchestrates data ingestion and preprocessing
- **DAGs**: 
  - `data_ingestion_dag.py`: Download and validate wine quality dataset
  - `model_training_dag.py`: Train and upload model to S3
- **Storage**: Raw data and trained models stored in S3

## Security Architecture

```mermaid
graph LR
    subgraph "IAM Roles & Policies"
        Admin[Admin User<br/>AdministratorAccess]
        Dev[Developer User<br/>Limited Permissions]
        
        subgraph "ECS Task Role"
            S3Policy[S3 Read Policy<br/>GetObject only]
            LogPolicy[CloudWatch Logs<br/>PutLogEvents]
            MetricPolicy[CloudWatch Metrics<br/>PutMetricData]
        end
    end
    
    Admin -->|manages| Infrastructure[Terraform Infrastructure]
    Dev -->|deploys| CICD[GitHub Actions]
    
    ECSTask[ECS Task] -->|assumes| S3Policy
    ECSTask -->|assumes| LogPolicy
    ECSTask -->|assumes| MetricPolicy
    
    style Admin fill:#f44336
    style Dev fill:#FF9800
    style S3Policy fill:#4CAF50
    style LogPolicy fill:#4CAF50
    style MetricPolicy fill:#4CAF50
```

### IAM Best Practices Implemented
- ✅ Separate admin and developer users
- ✅ Least-privilege policies (read-only S3 access for tasks)
- ✅ Service-specific roles (ECS task execution vs task role)
- ✅ CloudWatch permissions separated (logs vs metrics)

## Data Flow

```mermaid
sequenceDiagram
    participant Client
    participant ALB
    participant ECS as ECS Task (FastAPI)
    participant S3
    participant CW as CloudWatch
    
    Client->>ALB: POST /predict
    ALB->>ECS: Forward request
    
    alt Model not loaded
        ECS->>S3: GetObject wine-quality-model.pkl
        S3-->>ECS: Model artifact
        ECS->>ECS: Load model into memory
    end
    
    ECS->>ECS: Run prediction
    ECS->>CW: Publish metrics (request count, latency)
    ECS->>CW: Write logs
    ECS-->>ALB: Return prediction
    ALB-->>Client: JSON response
```

## Deployment Flow

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant GH as GitHub
    participant GHA as GitHub Actions
    participant ECR
    participant ECS
    
    Dev->>GH: git push main
    GH->>GHA: Trigger workflow
    
    GHA->>GHA: Run tests (pytest)
    
    alt Tests pass
        GHA->>GHA: Build Docker image
        GHA->>ECR: Push image
        GHA->>ECS: Update service (force new deployment)
        ECS->>ECR: Pull new image
        ECS->>ECS: Start new task
        ECS->>ECS: Health check passes
        ECS->>ECS: Stop old task
        GHA-->>Dev: ✅ Deployment successful
    else Tests fail
        GHA-->>Dev: ❌ Deployment blocked
    end
```

## Cost Optimization

| Component | Configuration | Monthly Cost (Est.) |
|-----------|--------------|---------------------|
| ECS Fargate | 0.25 vCPU, 512MB, 24/7 | ~$5-7 |
| Application Load Balancer | Single AZ | ~$16 |
| S3 Storage | <1 GB | <$0.10 |
| CloudWatch Logs | <1 GB | <$1 |
| CloudWatch Metrics | 5 custom metrics | $1.50 |
| **Total** | | **~$23-25/month** |

### Free Tier Benefits
- ✅ ECS Fargate: 20 GB-hours free (covers ~10 days)
- ✅ S3: 5 GB storage free
- ✅ CloudWatch: 10 custom metrics free (using 5)

## Technology Stack

| Layer | Technology |
|-------|-----------|
| **Infrastructure** | Terraform, AWS VPC, ECS Fargate, ALB |
| **Container** | Docker, ECR |
| **API** | FastAPI, Python 3.9, Uvicorn |
| **ML** | scikit-learn, pandas, numpy |
| **CI/CD** | GitHub Actions |
| **Monitoring** | CloudWatch Logs, Metrics, Dashboards |
| **Data Pipeline** | Apache Airflow, Docker Compose |
| **Storage** | AWS S3 |

## Related Documentation

- [AWS Setup Guide](./docs/aws-setup/)
- [Data Pipeline Documentation](./docs/data-pipeline/)
- [API Documentation](./docs/model-api/)
- [Troubleshooting Guide](./docs/troubleshooting/)
- [CloudWatch Setup](./docs/monitoring/cloudwatch-setup.md)
