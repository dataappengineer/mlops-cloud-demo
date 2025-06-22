# Documentation Overview

This folder contains guides and templates for setting up, securing, and managing your AWS-based MLOps project. Use these docs to ensure secure, efficient, and cost-effective cloud operations, and to document your process for future reference or sharing.

## Contents
- `aws_account_setup.md`: Step-by-step AWS account and IAM setup, including root user security and MFA
- `region_selection.md`: How to choose the best AWS region for your project
- `permissions_policies.md`: IAM group and policy recommendations for admin and least-privilege users
- `aws_services.md`: List of AWS services used and Free Tier constraints
- `cli_and_tools_setup.md`: Configure AWS CLI, VS Code, Terraform, and GitHub Actions for AWS access
- `security_checklist.md`: Quick checklist for AWS security hygiene (MFA, key rotation, least privilege, etc.)
- `billing_and_cost_management.md`: How to set up budgets, Free Tier usage alerts, and monitor costs
- `resource_cleanup.md`: How to identify and clean up unused AWS resources to minimize costs

## Subfolders by Project Phase
- `aws-setup/`: All AWS account, IAM, billing, and cost management docs
- `data-pipeline/`: Data ingestion, preprocessing, and pipeline setup
- `model-training/`: Model training, experiment tracking, and artifacts
- `deployment/`: Infrastructure as Code, deployment scripts, and cloud setup
- `monitoring/`: Monitoring, logging, and alerting setup
- `frontend-ui/`: Frontend and analytics UI documentation
- `ci-cd/`: CI/CD pipeline and automation docs
- `architecture/`: Architecture diagrams and high-level overviews

## How to Use
- Follow the setup guides in order for a secure and robust foundation
- Reference the checklist and cost management docs regularly to maintain best practices and avoid unexpected charges
- Use the subfolders to organize documentation for each phase of your MLOps project
- Update these docs as your project evolves or requirements change

---

_Last updated: June 21, 2025_