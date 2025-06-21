# AWS Account Setup and IAM Best Practices

## Step-by-Step Guide

1. **Create your AWS account and set up the root user.**
   - Use a strong, unique password for the root user.
   - **Enable Multi-Factor Authentication (MFA) for the root user immediately.**
   - Only use the root user for critical account and billing tasks.
2. **Log out of the root account and log in with your new IAM user** (in the `mlops-admins` group).
3. **Create a new group for least-privilege users** (e.g., `mlops-developers`) and assign only the permissions needed for development/deployment.
4. **Create a new IAM user for least-privilege access** and add it to this group.

## Usage
- Use the least-privilege user (or its access keys) for programmatic access (AWS CLI, Terraform, GitHub Actions, etc.).
- Never use your root account for daily work or automation.

## Summary
- Use your admin IAM user for setup and management.
- Use least-privilege IAM users for development, automation, and CI/CD integrations.
- Always keep access keys secure and rotate them regularly.
