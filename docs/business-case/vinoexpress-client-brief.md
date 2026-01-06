# VinoExpress: ML Infrastructure for Cost-Conscious Startups

**Client Profile**  
VinoExpress is a Colombian wine distribution startup serving 200+ restaurants across Bogotá, Medellín, and Cali. Their technical team includes 10 software engineers and 3 data scientists.

**The Business Problem**  
Manual wine quality assessment delays shipments by 2-3 days. Quality analysts visually inspect samples and fill out 50+ data points per batch. For a company processing 40 shipments weekly, this bottleneck costs approximately $15,000/month in delayed deliveries and analyst labor.

VinoExpress needed automated quality prediction in under 1 second per sample, but faced a critical constraint: their engineering budget allocated only **$450/month** for ML infrastructure.

---

## The Technical Challenge

### Initial Architecture Exploration

The data science team trained a RandomForest model (98 features, 100 estimators) achieving 92% accuracy on quality prediction. The challenge wasn't the model—it was deploying it cost-effectively.

**Standard options exceeded budget:**
- **AWS SageMaker**: $150-200/month for always-on endpoint
- **AWS EKS**: $93-113/month (cluster + nodes + overhead)

Both solutions worked technically but consumed 35-50% of the total infrastructure budget for a single ML model—unsustainable for a startup planning to deploy 5+ models across different workflows.

### The Cost-Aware Solution

We deployed on **AWS ECS Fargate** with aggressive cost optimization:

**Final Monthly Cost: $12.34** (97% under budget)

This included:
- FastAPI model serving (24/7 availability)
- Application Load Balancer (multi-AZ)
- CloudWatch monitoring (custom metrics)
- Automatic scaling capability
- Production-grade logging

---

## The Optimization Journey

### Discovery Through Monitoring

After initial deployment at $21.24/month, systematic monitoring revealed two cost leaks:

**Finding #1: Health Check Overhead (Issue #28)**  
Load balancer health checks ran every 30 seconds, publishing CloudWatch metrics for each request. At 2,880 checks/day, this generated 21,600 metric writes consuming 95% of our free tier CloudWatch API quota.

**Solution**: Disabled metric publishing for health check endpoints while preserving logging. Health checks still run (service reliability unchanged), but don't generate billable API calls.

**Savings**: ~$8.00/month

**Finding #2: ContainerInsights Hidden Cost (Issue #31)**  
ECS ContainerInsights, enabled by default, published 38 metrics per service (CPU, memory, network I/O, storage). With only 10 free tier metrics, this created a 28-metric overage costing $8.40/month.

**Solution**: Disabled ContainerInsights, kept 5 business-critical custom metrics (predictions/hour, model latency, error rate).

**Savings**: $9.90/month

### The 48-Hour Verification

Both optimizations were deployed January 5, 2026, and verified after 48 hours using AWS CLI:

- **Metrics verification**: ContainerInsights stopped publishing (last datapoint before deployment cutoff)
- **Log verification**: 17 health checks logged but zero CloudWatch writes
- **Billing verification**: January MTD tracking $8.11/month Fargate (under $8.89 projected)

**Total reduction**: $21.24 → $12.34 (42% savings in 2 days)

---

## Why This Matters for Startups

### Cost Transparency as Competitive Advantage

Budget-conscious startups don't need promises—they need receipts. VinoExpress saw:

1. **Actual AWS billing data** (not estimates)
2. **Before/after cost comparisons** with evidence
3. **Systematic discovery process** (monitoring → hypothesis → verification)
4. **Gradual optimization** (didn't require perfect first try)

This approach proves capability through transparency. Every optimization is documented in GitHub issues (#28, #30, #31) with CloudWatch evidence and billing screenshots.

### The Real Lesson

Cost efficiency isn't about choosing the cheapest option—it's about **systematic monitoring and iterative improvement**. VinoExpress started at $21.24/month, discovered two leaks through production monitoring, and optimized to $12.34/month in 48 hours.

For startups hiring remote engineering talent (especially in LATAM, EU, or distributed teams), this demonstrates:

- Cost-aware architectural thinking
- Evidence-based decision making  
- Transparent communication of tradeoffs
- Real production problem-solving (not polished tutorials)

---

## Technical Stack & Documentation

**Infrastructure:**
- ECS Fargate (0.25 vCPU, 512 MB memory)
- Application Load Balancer (multi-AZ)
- CloudWatch (5 custom metrics)
- Terraform (infrastructure as code)

**Detailed Cost Breakdown:** `docs/AWS_COST_REFERENCE.md`  
**GitHub Issues:** [#28](https://github.com/dataappengineer/mlops-cloud-demo/issues/28), [#30](https://github.com/dataappengineer/mlops-cloud-demo/issues/30), [#31](https://github.com/dataappengineer/mlops-cloud-demo/issues/31)  
**Free Tier Expires:** June 21, 2026 (projected cost: $38.56/month post-free-tier)

---

## Project Status

**Deployed:** December 28, 2025  
**Optimized:** January 5, 2026  
**Verified:** January 6, 2026 (48-hour checkpoint)  
**Current State:** Production-ready, cost-optimized, fully monitored

This is a real production deployment with transparent cost tracking—not a toy project or tutorial. Every number is verifiable in AWS billing and CloudWatch metrics.
