# IAM Groups and Permissions for MLOps

## Admin Group (`mlops-admins`)
- Attach the `AdministratorAccess` policy.
- Only add users who truly need full control (ideally just you, and only when necessary).

## Least-Privilege Group (`mlops-developers`)
Attach only the permissions needed for development and deployment:
- `AmazonS3FullAccess` (or restrict to specific buckets)
- `AmazonEC2ContainerRegistryFullAccess` (for Docker images)
- `AmazonECSFullAccess` (for Fargate/ECS)
- `AWSLambda_FullAccess` (if using Lambda)
- `CloudWatchLogsFullAccess` (for logs/monitoring)
- `IAMReadOnlyAccess` (to view roles, not edit)
- (Optional) `AWSCodeBuildDeveloperAccess`, `AWSCodePipelineFullAccess` for CI/CD

## Summary
- Use the admin group only for setup and emergencies.
- Use the least-privilege group for daily development and deployment.
- Always prefer the minimum permissions needed for each user or group.
- Enable MFA for all users.
