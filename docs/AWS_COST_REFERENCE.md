# AWS Cost Reference - MLOps Cloud Demo

**Last Updated**: January 5, 2026  
**AWS Account Created**: June 21, 2025  
**Free Tier Expires**: June 21, 2026

---

## Infrastructure Configuration

**Deployment**: ECS Fargate + Application Load Balancer in us-east-1

| Component | Configuration |
|-----------|--------------|
| **ECS Fargate Task** | 0.25 vCPU, 512 MB (0.5 GB) memory, Linux/x86 |
| **Application Load Balancer** | HTTP listener on port 80 |
| **CloudWatch Logs** | ~1 GB/month |
| **CloudWatch Metrics** | 5 custom metrics (ContainerInsights disabled) |
| **S3 Storage** | ~500 MB (model artifacts) |
| **VPC Public IPv4** | 2 Elastic IPs (both for ALB multi-AZ) |

**Deployed**: December 28, 2025  
**Runtime**: 24/7 continuous operation

---

## Verified Pricing (us-east-1)

### AWS Fargate (NO FREE TIER)
- **vCPU**: $0.04048 per vCPU-hour
- **Memory**: $0.004445 per GB-hour
- **Charged from first second of usage**

### Application Load Balancer (750 FREE HOURS/MONTH for 12 months)
- **ALB Hour**: $0.0225 per hour
- **LCU**: $0.008 per LCU-hour
- **Free Tier**: 750 hours + 15 LCUs per month

### VPC Public IPv4 (750 FREE HOURS/MONTH for 12 months)
- **Rate**: $0.005 per IP per hour
- **Free Tier**: 750 hours per month

### CloudWatch Logs (5 GB FREE for 12 months)
- **Ingestion**: $0.50 per GB
- **Free Tier**: 5 GB per month

### S3 Standard Storage (5 GB FREE for 12 months)
- **Storage**: $0.023 per GB-month
- **Free Tier**: 5 GB per month

### CloudWatch Metrics (10 FREE for 12 months)
- **Rate**: $0.30 per metric per month
- **Free Tier**: 10 custom metrics per month
- **Note**: ECS ContainerInsights generates 38 metrics if enabled

---

## Actual December 2025 Bill (4 days runtime)

**Billing Period**: December 28-31, 2025 (4 days / ~94 hours)

| Service | Usage | Cost |
|---------|-------|------|
| Fargate vCPU | 23.524 vCPU-hours (0.25 × 94 hrs) | $0.95 |
| Fargate Memory | 47.049 GB-hours (0.5 × 94 hrs) | $0.21 |
| Cost Explorer API | 1 request | $0.01 |
| **TOTAL** | | **$1.17** |

**All other services**: $0 (covered by free tier)

---

## Monthly Cost Projections (720 hours)

### Option 1: Current State - OPTIMIZED (NOW - June 2026)
**Free Tier Active** | **ContainerInsights Disabled**

| Service | Calculation | Monthly Cost |
|---------|------------|--------------|
| **Fargate vCPU** | 0.25 × 720 × $0.04048 | $7.29 |
| **Fargate Memory** | 0.5 × 720 × $0.004445 | $1.60 |
| ALB Hours | 720 hrs (FREE: 750 hrs) | $0.00 |
| ALB LCUs | ~1 LCU (FREE: 15 LCUs) | $0.00 |
| **VPC Public IPv4** | 2 IPs × 720 hrs - 750 free = 690 hrs × $0.005 | **$3.45** |
| CloudWatch Logs | 1 GB (FREE: 5 GB) | $0.00 |
| CloudWatch Metrics | 5 custom (FREE: 10) | $0.00 |
| S3 Storage | 0.5 GB (FREE: 5 GB) | $0.00 |
| **TOTAL** | | **$12.34/month** |

### Option 2: Pre-Optimization State (HISTORICAL)
**What costs WOULD BE with ContainerInsights enabled**

| Service | Calculation | Monthly Cost |
|---------|------------|--------------|
| **Fargate vCPU** | 0.25 × 720 × $0.04048 | $7.29 |
| **Fargate Memory** | 0.5 × 720 × $0.004445 | $1.60 |
| ALB Hours | 720 hrs (FREE: 750 hrs) | $0.00 |
| ALB LCUs | ~1 LCU (FREE: 15 LCUs) | $0.00 |
| **VPC Public IPv4** | 2 IPs × 720 hrs - 750 free = 690 hrs × $0.005 | **$3.45** |
| CloudWatch Logs | 1 GB (FREE: 5 GB) | $0.00 |
| **CloudWatch Metrics** | 43 metrics - 10 free = 33 × $0.30 | **$9.90** |
| S3 Storage | 0.5 GB (FREE: 5 GB) | $0.00 |
| **TOTAL** | | **$21.24/month** |

**Optimization Savings**: Disabling ContainerInsights saves **$9.90/month** ($21.24 → $12.34)

### Option 3: After Free Tier Expires (June 2026+)
**All Services at Standard Rates**

| Service | Calculation | Monthly Cost |
|---------|------------|--------------|
| **Fargate vCPU** | 0.25 × 720 × $0.04048 | $7.29 |
| **Fargate Memory** | 0.5 × 720 × $0.004445 | $1.60 |
| **ALB Hours** | 720 × $0.0225 | $16.20 |
| **ALB LCUs** | 1 × 720 × $0.008 | $5.76 |
| **VPC Public IPv4** | 2 × 720 × $0.005 | $7.20 |
| **CloudWatch Logs** | 1 GB × $0.50 | $0.50 |
| CloudWatch Metrics | 5 custom (first 10 free) | $0.00 |
| **S3 Storage** | 0.5 GB × $0.023 | $0.01 |
| **TOTAL** | | **$38.56/month** |

**Cost Increase after June 2026**: +$26.22/month (from $12.34 to $38.56)

---

## Services That Start Charging After June 2026

| Service | Free Tier Benefit | Post-Free-Tier Cost |
|---------|------------------|---------------------|
| Application Load Balancer | 750 hours/month | $16.20/month |
| ALB LCUs | 15 LCUs/month | $5.76/month |
| VPC Public IPv4 | 750 hours/month | $7.20/month |
| CloudWatch Logs | 5 GB/month | $0.50/month |
| S3 Storage | 5 GB/month | $0.01/month |
| **TOTAL NEW CHARGES** | | **$29.67/month** |

**Note**: Current optimized state ($12.34/month) already includes $3.45 VPC overage, so actual increase is $26.22/month

---

## Cost Optimization Strategies

### Strategy 1: Disable ContainerInsights ✅ IMPLEMENTED
- **Before**: $21.24/month (with 38 ContainerInsights metrics)
- **After**: $12.34/month (with 5 custom metrics)
- **Savings**: $9.90/month
- **Date**: January 5, 2026 (Issue #31)
- **Impact**: Eliminated unnecessary container-level monitoring for single-container demo

### Strategy 2: Fargate Spot (70% discount)
- **Current Fargate**: $8.89/month
- **With Fargate Spot**: $2.67/month
- **Savings**: $6.22/month
- **Note**: Workload must tolerate interruptions

### Strategy 3: Compute Savings Plan (50% discount)
- **Current Fargate**: $8.89/month
- **With 1-year plan**: $4.45/month
- **Savings**: $4.44/month
- **Note**: 1-3 year commitment required

### Strategy 4: Stop Service When Idle
- **Cost when running**: $12.34/month (now), $38.56/month (after June)
- **Cost when stopped**: $0.00/month
- **Use case**: Stop during nights/weekends when not demoing

### Strategy 5: Remove ALB (Post-June 2026)
- **Savings**: $21.96/month (ALB + LCUs)
- **Alternative**: Direct Fargate access with public IP
- **Tradeoff**: Lose load balancing and health checks

---

## Key Findings & Mysteries

### ✅ Verified Facts
1. **Fargate has NO free tier** - charges apply from first second
2. **ALB has 750 hours/month free tier** - enough for 24/7 operation
3. **December bill ($1.17) is accurate** - Fargate only
4. **Monthly projection ($12.34) is optimized** - verified by Amazon Q + AWS CLI
5. **VPC has 2 Elastic IPs (not 3)** - both for ALB multi-AZ, verified Jan 5, 2026
6. **ContainerInsights generates 38 metrics** - causes $9.90/month overage when enabled
7. **CloudWatch optimization effective** - API-level metrics reduced to zero (Issue #28)

### 🎯 Cost Evolution Timeline
- **Dec 28, 2025**: Initial deployment, no optimization ($21.24/month projected)
- **Jan 4, 2026**: API CloudWatch optimization (Issue #28, PR #29 merged)
- **Jan 5, 2026**: ContainerInsights disabled (Issue #31) → **$12.34/month achieved**

### 🤔 Unsolved Mystery: ALB Hour Discrepancy
- **Expected ALB hours in December**: 79 hours (Dec 28 4:49 PM - Dec 31 11:59 PM)
- **Shown in Free Tier Dashboard**: 27 hours
- **Discrepancy**: 52 hours missing

**Possible Explanations**:
1. Free Tier Dashboard updates with lag (48-72 hour delay)
2. Dashboard shows usage from different billing period cutoff
3. Partial-hour rounding or aggregation method
4. Dashboard bug (ALB is confirmed "active" via CLI)

**Impact**: None - well under 750-hour limit regardless

**Status**: ALB is running correctly, charges will remain $0 until June 2026

---

## MTD (Month-To-Date) Forecasted Usage

**MTD = Month-To-Date**: Cumulative usage from the 1st day of current month to today

**Forecasted Usage %**: AWS prediction of what % of free tier you'll consume by month-end based on current usage rate

**Example Calculation**:
- You used 27 ALB hours in 4 days (Dec 28-31)
- Extrapolated to 31 days: 27 ÷ 4 × 31 = 209 hours
- Free tier limit: 750 hours
- Forecasted usage: 209 ÷ 750 = 27.9%

**Your Dashboard Shows**:
- ALB: 3.58% MTD forecasted usage
- VPC IPv4: 12.75% MTD forecasted usage

Both are well below 100%, meaning you'll stay within free tier limits for January.

---

## Decision Matrix

### Keep Running 24/7 Until June 2026?
**Cost**: $12.34/month × 5 months = $61.70 total  
**Benefit**: Live portfolio showcase, professional demo URL, CloudWatch metrics  
**Recommendation**: ✅ **YES** - Very affordable for portfolio value

### After June 2026 Options

| Option | Monthly Cost | When to Use |
|--------|--------------|-------------|
| **Keep Running + Fargate Spot** | $32.34 | Active job search |
| **Stop/Start on Demand** | $0-38.56 | Occasional demos |
| **Destroy Infrastructure** | $0.00 | After landing job |

---

## Quick Commands

### Check Current Costs
```bash
aws ce get-cost-and-usage \
  --time-period Start=2026-01-01,End=2026-01-31 \
  --granularity MONTHLY \
  --metrics "BlendedCost" \
  --profile mlops-admin \
  --region us-east-1
```

### Stop Service (Scale to 0)
```bash
aws ecs update-service \
  --cluster mlops-demo-dev-cluster \
  --service mlops-demo-dev-model-api \
  --desired-count 0 \
  --profile mlops-admin \
  --region us-east-1
```

### Start Service (Scale to 1)
```bash
aws ecs update-service \
  --cluster mlops-demo-dev-cluster \
  --service mlops-demo-dev-model-api \
  --desired-count 1 \
  --profile mlops-admin \
  --region us-east-1
```

---

## Sources & Verification

- **Amazon Q Analysis**: January 1, 2026 (3 queries), January 5, 2026 (2 queries for Issue #30)
- **AWS Pricing Pages**: Fargate, ALB, VPC, CloudWatch (Logs + Metrics), S3
- **AWS Free Tier Dashboard**: Real-time usage tracking
- **December 2025 Bill**: Actual charges validated
- **AWS CLI Verification**: `aws cloudwatch list-metrics`, `aws ec2 describe-addresses` (Jan 5, 2026)
- **Cost Calculations**: Python-based analysis of 24h checkpoint data (Issue #30)

**Confidence Level**: ✅ HIGH - All numbers triple-verified (terminal + Amazon Q + AWS CLI)

---

## Related Issues & PRs

- **Issue #28**: CloudWatch Cost Optimization - Initial API-level fixes
- **PR #29**: CloudWatch optimization implementation (merged Jan 4, 2026)
- **Issue #30**: 24h Checkpoint - Discovered ContainerInsights overage
- **Issue #31**: Disable ContainerInsights - $9.90/month savings
- **Project Board**: https://github.com/users/dataappengineer/projects/9
