# ML Model Serving Architecture Decision Matrix

**Decision Context**: Deploying a RandomForest model (98 features, 100 estimators) for a startup with <$450/month infrastructure budget requiring 24/7 availability and <1 second response time.

**Date**: January 2026  
**AWS Region**: us-east-1  
**Free Tier Status**: Active until June 21, 2026

---

## Executive Summary

**Selected Architecture**: AWS ECS Fargate  
**Monthly Cost**: $12.34 (during free tier) | $38.56 (post-free-tier)  
**Key Rationale**: 68-92% cost savings vs alternatives while maintaining production quality

---

## Architecture Comparison Matrix

| Criterion | AWS SageMaker | AWS EKS | AWS ECS Fargate (Selected) |
|-----------|---------------|---------|---------------------------|
| **Monthly Cost (Free Tier)** | $150-200 | $93-113 | **$12.34** ✅ |
| **Monthly Cost (Post-Free-Tier)** | $150-200 | $93-113 | **$38.56** ✅ |
| **Operational Complexity** | Low | High | **Medium** ✅ |
| **Time to Production** | 2-3 days | 1-2 weeks | **1-2 days** ✅ |
| **Scaling Capability** | Excellent | Excellent | Good |
| **Multi-Model Support** | Native | Excellent | Manual |
| **Minimum Viable Scale** | 1 endpoint | 2 nodes | **1 task** ✅ |
| **Ops Overhead** | Low | High | **Low** ✅ |
| **Learning Curve** | Medium | Steep | **Gentle** ✅ |

---

## Detailed Cost Breakdown

### Option 1: AWS SageMaker Endpoint

**Monthly Cost: $150-200**

| Component | Configuration | Monthly Cost |
|-----------|--------------|--------------|
| Endpoint Instance | ml.t3.medium (2 vCPU, 4 GB) | $52.56 |
| Model Storage | 500 MB S3 | $0.01 |
| CloudWatch Logs | 5 GB | $0.00 (free tier) |
| Data In/Out | 10 GB transfer | $0.90 |
| **Minimum Total** | | **$53.47** |

**Typical Production Setup: $150-200/month**
- Multi-AZ deployment (2x instances): $105.12
- Autoscaling (avg 3 instances): $157.68
- Additional monitoring/logging: $10-20
- Data transfer at scale: $20-30

**Pros:**
- ✅ Native A/B testing and model versioning
- ✅ Built-in monitoring and autoscaling
- ✅ Minimal operational overhead
- ✅ Optimized for ML workloads

**Cons:**
- ❌ 12-15x more expensive than ECS Fargate
- ❌ Overkill for single-model deployment
- ❌ Minimum instance costs apply even at low traffic

**Best For:**
- Multiple models requiring frequent updates
- A/B testing across model versions
- Organizations with >$500/month ML infrastructure budget
- Teams lacking DevOps expertise

---

### Option 2: AWS EKS (Kubernetes)

**Monthly Cost: $93-113**

| Component | Configuration | Monthly Cost |
|-----------|--------------|--------------|
| EKS Control Plane | Fixed per cluster | $72.00 |
| Worker Nodes | t3.small (2 nodes) | $14.38 |
| Application Load Balancer | 1 ALB + minimal LCUs | $16.20 |
| VPC Public IPv4 | 2 Elastic IPs | $3.45 |
| CloudWatch Logs | 2 GB | $0.00 (free tier) |
| S3 Storage | 500 MB | $0.00 (free tier) |
| **Minimum Total** | | **$106.03** |

**Typical Production Setup: $93-113/month**
- EKS Control Plane: $72.00
- 2x t3.small nodes (HA): $29.95
- ALB + minimal traffic: $16.20
- CloudWatch/VPC/S3: $3.45
- **During Free Tier**: $93.08 (ALB free)
- **Post-Free-Tier**: $113.03

**Pros:**
- ✅ Industry-standard orchestration (Kubernetes)
- ✅ Excellent for multi-service deployments
- ✅ Strong ecosystem (Helm, operators, service mesh)
- ✅ Portable across cloud providers

**Cons:**
- ❌ 8-9x more expensive than ECS Fargate
- ❌ $72/month control plane cost regardless of usage
- ❌ Requires Kubernetes expertise
- ❌ Overkill for single containerized model
- ❌ Higher operational complexity (node management, upgrades)

**Best For:**
- Microservices architecture (5+ services)
- Multi-environment deployments (dev/staging/prod)
- Teams with Kubernetes expertise
- Organizations planning cloud portability
- ML pipelines with complex orchestration

---

### Option 3: AWS ECS Fargate (Selected)

**Monthly Cost: $12.34 (free tier) | $38.56 (post-free-tier)**

#### During Free Tier (Until June 2026)

| Component | Configuration | Monthly Cost |
|-----------|--------------|--------------|
| Fargate vCPU | 0.25 vCPU × 720 hrs × $0.04048 | $7.29 |
| Fargate Memory | 0.5 GB × 720 hrs × $0.004445 | $1.60 |
| Application Load Balancer | 720 hours (FREE: 750 hrs) | $0.00 |
| ALB LCUs | ~1 LCU (FREE: 15 LCUs) | $0.00 |
| VPC Public IPv4 | 2 IPs × 720 hrs - 750 free = 690 hrs × $0.005 | $3.45 |
| CloudWatch Logs | 1 GB (FREE: 5 GB) | $0.00 |
| CloudWatch Metrics | 5 custom (FREE: 10) | $0.00 |
| S3 Storage | 500 MB (FREE: 5 GB) | $0.00 |
| **TOTAL** | | **$12.34** |

#### After Free Tier (June 2026+)

| Component | Configuration | Monthly Cost |
|-----------|--------------|--------------|
| Fargate vCPU | 0.25 × 720 × $0.04048 | $7.29 |
| Fargate Memory | 0.5 × 720 × $0.004445 | $1.60 |
| Application Load Balancer | 720 × $0.0225 | $16.20 |
| ALB LCUs | 1 × 720 × $0.008 | $5.76 |
| VPC Public IPv4 | 2 × 720 × $0.005 | $7.20 |
| CloudWatch Logs | 1 GB × $0.50 | $0.50 |
| S3 Storage | 0.5 GB × $0.023 | $0.01 |
| **TOTAL** | | **$38.56** |

**Pros:**
- ✅ **68-92% cheaper** than alternatives
- ✅ No cluster management overhead
- ✅ Pay only for task runtime (no idle costs)
- ✅ Fast deployment (Docker + Terraform)
- ✅ Production-grade (multi-AZ ALB, health checks, autoscaling)
- ✅ Familiar tooling (Docker, no Kubernetes required)

**Cons:**
- ❌ Manual orchestration for multi-model deployments
- ❌ Less sophisticated than SageMaker for ML-specific features
- ❌ No native A/B testing (requires custom implementation)

**Best For:**
- Single-service deployments (1-3 models)
- Startups with <$450/month infrastructure budget
- Teams prioritizing cost efficiency over orchestration complexity
- MVP/demo deployments requiring production quality

---

## Decision Rationale

### Why ECS Fargate Won

**1. Cost Efficiency at Low Scale**
- $12.34/month vs $150-200 (SageMaker) or $93-113 (EKS)
- 92% savings vs SageMaker, 87% savings vs EKS
- Critical for startups where $100-150/month = 1-2 days of engineer time

**2. Operational Simplicity**
- No Kubernetes learning curve (vs EKS)
- No ML-specific abstractions to learn (vs SageMaker)
- Standard Docker containers + Terraform IaC
- Minimal ops overhead for single-model deployment

**3. Production Quality Maintained**
- Multi-AZ Application Load Balancer
- Health checks every 30 seconds
- CloudWatch logging and custom metrics
- Automatic task recovery on failure

**4. Proven Through Optimization**
- Started at $21.24/month, optimized to $12.34/month (42% reduction)
- Demonstrated systematic cost monitoring (Issues #28, #31)
- Evidence-based optimization (CloudWatch metrics, AWS CLI verification)
- Real production deployment, not theoretical

---

## Graduation Path: When to Migrate

### Stick with ECS Fargate When:
- ✅ Serving 1-3 models
- ✅ Traffic <10,000 requests/day
- ✅ Team size <15 engineers
- ✅ Budget <$500/month for ML infrastructure
- ✅ Single-region deployment

### Consider EKS When:
- 🔄 Deploying 5+ microservices (not just ML models)
- 🔄 Multi-region requirements
- 🔄 Team has Kubernetes expertise
- 🔄 Complex orchestration needs (cron jobs, batch processing, service mesh)
- 🔄 Budget >$500/month and rising

### Consider SageMaker When:
- 🔄 Frequent model updates (daily/weekly retraining)
- 🔄 A/B testing across model versions
- 🔄 Multi-model endpoints (>5 models)
- 🔄 Budget >$1,000/month for ML infrastructure
- 🔄 Team lacks DevOps skills

---

## Migration Cost Comparison

### Current State: ECS Fargate
**Cost**: $12.34/month (free tier) → $38.56/month (post-free-tier)  
**Setup**: Complete, optimized, production-ready

### Migration to EKS
**Cost Impact**: +$54.47/month (free tier) → +$74.47/month (post-free-tier)  
**Migration Effort**: 40-60 hours (Kubernetes learning, Helm charts, node configuration)  
**Break-Even**: Only worth it when deploying 5+ services

### Migration to SageMaker
**Cost Impact**: +$137.66/month (free tier) → +$111.44/month (post-free-tier)  
**Migration Effort**: 20-30 hours (model packaging, endpoint configuration, SDK changes)  
**Break-Even**: Only worth it with frequent model updates or A/B testing needs

---

## Real-World Context: VinoExpress Case Study

**Client Budget**: $450/month total infrastructure  
**ML Portion**: $12.34/month (2.7% of budget)  
**Remaining Budget**: $437.66 for databases, storage, compute, networking

**Alternative Scenarios:**
- **With SageMaker**: $150/month (33% of budget) - unsustainable for 5+ model roadmap
- **With EKS**: $93/month (21% of budget) - overkill for single model

**Result**: ECS Fargate enabled VinoExpress to deploy production ML under 3% of infrastructure budget, leaving room for future services.

---

## Technical Stack Reference

**Current Implementation:**
- ECS Fargate (0.25 vCPU, 512 MB memory)
- Application Load Balancer (multi-AZ)
- CloudWatch (5 custom metrics, 1 GB logs/month)
- Terraform (infrastructure as code)
- FastAPI (model serving framework)
- Docker (containerization)

**Detailed Cost Documentation:** `docs/AWS_COST_REFERENCE.md`  
**Optimization Journey:** Issues [#28](https://github.com/dataappengineer/mlops-cloud-demo/issues/28), [#30](https://github.com/dataappengineer/mlops-cloud-demo/issues/30), [#31](https://github.com/dataappengineer/mlops-cloud-demo/issues/31)

---

## Decision Summary

| Criteria | Weight | SageMaker | EKS | ECS Fargate |
|----------|--------|-----------|-----|-------------|
| Cost Efficiency | 40% | 2/10 | 4/10 | **10/10** ✅ |
| Operational Simplicity | 30% | 8/10 | 3/10 | **9/10** ✅ |
| Time to Production | 20% | 7/10 | 4/10 | **9/10** ✅ |
| Scalability | 10% | 10/10 | 10/10 | 7/10 |
| **Weighted Score** | | **5.6/10** | **4.2/10** | **9.3/10** ✅ |

**For single-model deployments with budget constraints, ECS Fargate is the clear winner.**

---

**Last Updated**: January 6, 2026  
**Status**: Production-deployed and cost-optimized
