# CI/CD Setup Instructions

## GitHub Secrets Configuration

To enable automated deployments, add the following secrets to your GitHub repository:

**Settings → Secrets and variables → Actions → New repository secret**

### Required Secrets

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `AWS_ACCESS_KEY_ID` | `AKIA...` | AWS access key for mlops-admin user |
| `AWS_SECRET_ACCESS_KEY` | `xxx...` | AWS secret key for mlops-admin user |
| `AWS_REGION` | `us-east-1` | AWS region for deployment |
| `ECR_REPOSITORY` | `mlops-demo-model-api` | ECR repository name |
| `ECS_CLUSTER` | `mlops-demo-dev-cluster` | ECS cluster name |
| `ECS_SERVICE` | `mlops-demo-dev-model-api` | ECS service name |

### How to Get AWS Credentials

```bash
# Use your mlops-admin profile credentials
aws configure get aws_access_key_id --profile mlops-admin
aws configure get aws_secret_access_key --profile mlops-admin
```

## Workflow Trigger

The CI/CD pipeline automatically runs when:
- Code is pushed to `main` branch
- Changes are made to `model-api/` directory
- Workflow file is modified

Manual trigger is also available via GitHub Actions UI.

## Workflow Steps

1. **Test** - Run pytest on model-api
2. **Build** - Build Docker image
3. **Push** - Push to Amazon ECR
4. **Deploy** - Update ECS service with new image
5. **Wait** - Wait for service to stabilize

## Testing Locally

```bash
cd model-api
pip install pytest pytest-cov httpx
pytest tests/ -v --cov=app
```

## Monitoring Deployments

- GitHub Actions tab shows workflow runs
- AWS ECS Console shows deployment status
- CloudWatch Logs show application logs

## Troubleshooting

**Issue**: Workflow fails with "AccessDenied"
- **Solution**: Verify GitHub Secrets are set correctly with mlops-admin credentials

**Issue**: Tests fail
- **Solution**: Run tests locally first: `pytest tests/ -v`

**Issue**: Deployment timeout
- **Solution**: Check ECS task logs in CloudWatch for errors

## Status Badge

Add to README.md:
```markdown
![Deploy Status](https://github.com/dataappengineer/mlops-cloud-demo/actions/workflows/deploy-model-api.yml/badge.svg)
```
