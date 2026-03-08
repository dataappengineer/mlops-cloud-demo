# Migration Reference — mlops-cloud-demo → diagnostic-web-app

This document lists all assets from mlops-cloud-demo that are being 
recycled into the diagnostic-web-app PE demo stack.

## AWS Resources (DO NOT DELETE YET)

| Resource | Name/ARN | Used By |
|---|---|---|
| S3 Bucket | `mlops-processed-data-982248023588` | Airflow DAGs, model artifacts |
| IAM Role (task execution) | `arn:aws:iam::982248023588:role/mlops-demo-dev-ecs-execution-role` | ECS task execution |
| IAM Role (task) | `arn:aws:iam::982248023588:role/mlops-demo-dev-ecs-task-role` | FastAPI S3 model loading |
| ECR Repository | `mlops-demo-model-api` | Docker images (can be reused or Agent B creates new) |
| ECS Cluster | `mlops-demo-dev-cluster` | Scaled to 0 — do not destroy |
| ECS Service | `mlops-demo-dev-model-api` | Scaled to 0 tasks |
| ALB | `mlops-demo-dev-alb-*` | Can be destroyed after diagnostic-web-app has its own |
| VPC | `vpc-0ed062a8ee499c147` | Reference for Agent B's Terraform |

## Code Assets to Copy to diagnostic-web-app

| Source Path | Destination in diagnostic-web-app | Notes |
|---|---|---|
| `infrastructure/terraform/` | `infrastructure/terraform/` | Update project_name var |
| `.github/workflows/deploy-model-api.yml` | `.github/workflows/deploy-pe-api.yml` | Update ECR/ECS refs |
| `data-pipeline/dags/data_ingestion_dag.py` | `framework/demo-mvp/data-pipeline/dags/portco_ingest_dag.py` | Replace data source |
| `data-pipeline/dags/model_training_dag.py` | `framework/demo-mvp/data-pipeline/dags/pe_model_training_dag.py` | Replace model |
| `data-pipeline/Dockerfile` | `framework/demo-mvp/data-pipeline/Dockerfile` | Copy verbatim |
| `data-pipeline/docker-compose.yml` | `framework/demo-mvp/data-pipeline/docker-compose.yml` | Update volume paths |
| `data-pipeline/requirements.txt` | `framework/demo-mvp/data-pipeline/requirements.txt` | Copy verbatim |
| `model-api/` (entire folder) | `framework/demo-mvp/model-api/` | Strip wine model, keep scaffold |

## S3 Folder Structure for PE Demo

Agent B will create these prefixes in the existing bucket:
- `s3://mlops-processed-data-982248023588/portco-data/raw/`
- `s3://mlops-processed-data-982248023588/portco-data/clean/`
- `s3://mlops-processed-data-982248023588/portco-data/dirty/`
- `s3://mlops-processed-data-982248023588/models/pe-demo/`

## IAM Notes for Agent B

The existing IAM task role has `s3:GetObject` and `s3:PutObject` on the bucket.
Agent B can reuse the same role ARN — just reference it in their Terraform.

**Execution Role ARN**: `arn:aws:iam::982248023588:role/mlops-demo-dev-ecs-execution-role`  
**Task Role ARN**: `arn:aws:iam::982248023588:role/mlops-demo-dev-ecs-task-role`

## Current Status (March 8, 2026)

- ✅ ECS service scaled to 0 tasks (desiredCount = 0)
- ✅ Fargate compute cost: $0/month
- ✅ S3 bucket retained and accessible
- ✅ IAM roles retained for Agent B reuse
- ⏳ Waiting for Agent B to confirm their infrastructure is live

## Decommission Checklist (Run AFTER Agent B confirms their stack is live)

- [ ] `terraform destroy` — removes VPC, ALB, ECS cluster, ECR (NOT S3, NOT IAM roles)
- [ ] Delete ECR images (they'll be recreated by Agent B's CI/CD)  
- [ ] Archive this GitHub repo (Settings → Archive repository)
- [ ] Confirm diagnostic-web-app has its own ALB before destroying this one
- [ ] Final cost verification: Confirm monthly AWS costs drop to ~$0.50 (S3 storage only)

## Cost Impact

**Before migration** (Feb 2026): $7.89/month  
**After ECS scale-down** (March 8, 2026): ~$2-3/month (VPC NAT Gateway + S3)  
**After terraform destroy**: ~$0.50/month (S3 storage only)  
**After Agent B's stack is live**: Their costs ~$26/month (separate from this)

Total savings: ~$11.50/month by decommissioning wine quality demo while preserving infrastructure knowledge for new PE demo.
