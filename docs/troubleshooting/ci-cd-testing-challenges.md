# CI/CD Testing Challenges & Solutions

## Context
After implementing GitHub Actions CI/CD pipeline (PR #27), tests failed in the automated environment despite passing locally. This document captures the debugging journey and solutions.

## Challenge 1: Health Check Status Values

### Problem
```
FAILED tests/test_api.py::TestHealthEndpoint::test_health_endpoint_structure
AssertionError: assert 'degraded' in ['healthy', 'unhealthy']
```

### Root Cause
The health check endpoint returns three possible states:
- `"healthy"` - All systems operational
- `"degraded"` - Partial functionality (e.g., S3 accessible but model not loaded)
- `"unhealthy"` - Critical failures

Tests only checked for `healthy` or `unhealthy`, but the CI environment returned `degraded` because the model couldn't load from S3 without credentials.

### Solution
Updated test assertion to include all valid states:
```python
assert data["status"] in ["healthy", "unhealthy", "degraded"]
```

### Lesson Learned
**Test for actual system behavior, not ideal behavior.** The `degraded` state is a feature, not a bug - it allows the API to remain partially operational when external dependencies fail.

---

## Challenge 2: Mocking AWS Dependencies

### Problem
```
ERROR app.services.model_service:model_service.py:145 Failed to load model: 
AWS credentials not found. Please configure AWS credentials.
FAILED tests/test_api.py::TestPredictionEndpoint::test_predict_endpoint_accepts_valid_input
assert 500 == 200
```

### Root Cause
Prediction tests were failing because:
1. GitHub Actions runner has no AWS credentials (by design - we don't want tests hitting real S3)
2. FastAPI's `TestClient` triggers startup events that attempt to load the model from S3
3. Initial mocking approach didn't work because `predict()` is an async method

### Solution Evolution

**Attempt 1: Environment variables only** ❌
```python
os.environ['MODEL_BUCKET'] = 'test-bucket'
# Still failed - S3 connection attempted
```

**Attempt 2: Patch the method directly** ❌
```python
@patch('app.services.model_service.ModelService.predict')
def test_predict_endpoint(mock_predict):
    mock_predict.return_value = {...}  # Doesn't work for async
```

**Attempt 3: AsyncMock with pytest fixture** ✅
```python
@pytest.fixture
def mock_model_service():
    with patch('app.main.model_service') as mock:
        mock.predict = AsyncMock(return_value={
            "prediction": 5,
            "confidence": 0.98,
            "model_version": "1.0"
        })
        mock.load_model = AsyncMock()
        mock.model_loaded = True
        yield mock

def test_predict_endpoint(mock_model_service):
    # Test uses mocked service
```

### Key Insights
1. **Mock the instance, not the class**: `app.main.model_service` is the global instance used by endpoints
2. **Use AsyncMock for async methods**: Regular `Mock` doesn't work with `async def`
3. **Pytest fixtures for reusable mocks**: Cleaner than decorators when mocking multiple methods
4. **Mock startup behavior**: `load_model` also needs mocking to prevent S3 calls during TestClient initialization

---

## Challenge 3: API Response Structure Mismatch

### Problem
```
FAILED tests/test_api.py::TestRootEndpoint::test_root_endpoint_returns_welcome_message
AssertionError: assert 'message' in {...}
```

### Root Cause
Test expected a simple `{"message": "..."}` response, but the actual root endpoint returns a structured response:
```json
{
  "name": "Wine Quality Prediction API",
  "description": "ML-powered wine quality prediction service",
  "endpoints": {...},
  "model_info": {...}
}
```

### Solution
Update test to match actual API contract:
```python
assert "name" in data
assert "Wine Quality" in data["name"] or "API" in data["name"]
```

### Lesson Learned
**Write tests after implementing the API, not before.** We wrote tests based on assumptions rather than actual implementation. Integration tests should validate real behavior.

---

## Testing Strategy for FastAPI + AWS

### Best Practices Learned

1. **Separate unit and integration tests**
   - Unit tests: Mock all external dependencies (S3, model inference)
   - Integration tests: Use LocalStack or test AWS resources

2. **Use TestClient lifecycle management**
   ```python
   with TestClient(app) as client:
       # Properly handles startup/shutdown events
   ```

3. **Mock at the right level**
   - ✅ Mock service instances (`app.main.model_service`)
   - ❌ Don't mock low-level libraries (`boto3`)

4. **Test environment configuration**
   ```python
   os.environ['ENVIRONMENT'] = 'test'  # Before importing app
   ```

5. **Async test utilities**
   - Use `AsyncMock` for async functions
   - Use `pytest-asyncio` for native async test support

---

## CI/CD Workflow Evolution

### Iteration 1: Basic workflow (Failed)
- Tests assumed AWS credentials available
- No mocking strategy

### Iteration 2: Environment variables (Failed)
- Added test environment variables
- Still attempted real AWS connections

### Iteration 3: Mocked services (Success)
- AsyncMock for model service
- Pytest fixtures for reusability
- Isolated tests from external dependencies

### Final Workflow
```yaml
jobs:
  test:
    - Set up Python
    - Install dependencies (pytest, httpx)
    - Run tests (with mocked services)
  
  deploy:
    needs: test  # Only runs if tests pass
    - Build Docker image
    - Push to ECR (uses real AWS credentials from secrets)
    - Deploy to ECS
```

---

## Portfolio Value

This debugging journey demonstrates:

1. **Problem-solving methodology**: Systematic approach to test failures
2. **Understanding async Python**: Proper mocking of async methods
3. **CI/CD best practices**: Separating test and deployment concerns
4. **AWS security**: Not exposing credentials in test environments
5. **Documentation**: Capturing lessons learned for future reference

**Key Takeaway**: The struggle and iteration process is more valuable than perfect code on the first try. It shows real-world debugging skills.

---

## Challenge 4: CloudWatch IAM Permissions

### Problem
```
ERROR:app.utils.cloudwatch:Failed to publish metrics to CloudWatch: 
An error occurred (AccessDenied) when calling the PutMetricData operation: 
User: arn:aws:sts::982248023588:assumed-role/mlops-demo-dev-ecs-task-role 
is not authorized to perform: cloudwatch:PutMetricData
```

Dashboard showed "No data available" despite code being deployed successfully.

### Root Cause
The ECS task role had permissions for:
- ✅ S3 access (GetObject, ListBucket)
- ✅ CloudWatch Logs (CreateLogGroup, PutLogEvents)
- ❌ CloudWatch Metrics (PutMetricData) - **MISSING**

When the application called `cloudwatch_publisher.publish_metrics()`, boto3 failed silently and logged the AccessDenied error.

### Solution
Added new IAM policy to Terraform ([iam.tf](../../infrastructure/terraform/iam.tf)):

```hcl
resource "aws_iam_role_policy" "ecs_task_metrics_policy" {
  name = "${var.project_name}-${var.environment}-metrics-access"
  role = aws_iam_role.ecs_task_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "cloudwatch:PutMetricData"
        ]
        Resource = "*"
      }
    ]
  })
}
```

Applied with:
```bash
terraform apply -auto-approve
aws ecs update-service --force-new-deployment  # Pick up new IAM permissions
```

### Key Insights

1. **IAM is attached to tasks, not services**: Changing IAM policies requires restarting tasks
2. **Test IAM early**: Check CloudWatch Logs for AccessDenied errors immediately after deployment
3. **Metrics vs Logs**: CloudWatch has separate permissions for logs (PutLogEvents) and metrics (PutMetricData)
4. **Resource = "*" for metrics**: Unlike S3/ECR, CloudWatch metrics don't require specific resource ARNs

### Debugging Process
1. Checked CloudWatch dashboard → "No data available"
2. Checked CloudWatch Logs → Found AccessDenied errors
3. Identified missing IAM permission from error message
4. Added policy to Terraform
5. Applied infrastructure change
6. Forced ECS redeployment
7. Verified metrics started flowing to dashboard

---

## Related Documentation
- [CI/CD Setup Guide](../../.github/CI_CD_SETUP.md)
- [GitHub Actions Workflow](../../.github/workflows/deploy-model-api.yml)
- [Test Suite](../../model-api/tests/test_api.py)

**Status**: Resolved - All tests passing in GitHub Actions
**Date**: December 29, 2025
