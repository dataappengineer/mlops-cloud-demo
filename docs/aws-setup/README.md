# AWS Setup Documentation Overview

This folder contains all guides and templates for securely setting up, managing, and monitoring your AWS account and cloud costs for your MLOps project. Follow these docs to ensure your AWS environment is secure, cost-effective, and well-documented.

## Contents
- `aws_account_setup.md`: Step-by-step AWS account creation, root user security, and IAM setup
- `region_selection.md`: How to choose the best AWS region for your project
- `permissions_policies.md`: IAM group and policy recommendations for admin and least-privilege users
- `aws_services.md`: List of AWS services used and Free Tier constraints
- `cli_and_tools_setup.md`: How to configure AWS CLI, VS Code, Terraform, and GitHub Actions for AWS access
- `security_checklist.md`: Quick checklist for AWS security hygiene (MFA, key rotation, least privilege, etc.)
- `billing_and_cost_management.md`: How to set up budgets, Free Tier usage alerts, and monitor costs
- `resource_cleanup.md`: How to identify and clean up unused AWS resources to minimize costs
- `cloudwatch_vs_billing_alerts.md`: When to use CloudWatch alarms vs. Free Tier/Billing alerts, and how to set them up

## How to Use This Folder
1. **Start with `aws_account_setup.md`** to create your AWS account, secure the root user, and set up IAM users and groups.
2. **Review `region_selection.md`** to select the most appropriate AWS region for your needs.
3. **Follow `permissions_policies.md`** to assign the right permissions to your admin and developer groups.
4. **Consult `aws_services.md`** to understand which AWS services you’ll use and their Free Tier limits.
5. **Use `cli_and_tools_setup.md`** to configure your local and CI/CD tools for AWS access.
6. **Regularly check `security_checklist.md`** to maintain strong security practices.
7. **Monitor your spending with `billing_and_cost_management.md`** and set up all recommended alerts.
8. **Periodically review `resource_cleanup.md`** to ensure you’re not paying for unused resources.
9. **Read `cloudwatch_vs_billing_alerts.md`** to understand the difference between CloudWatch alarms and AWS billing alerts, and decide if you need more granular monitoring.

Keep this folder updated as your project evolves, and use it as a reference for onboarding new team members or writing technical articles about your cloud setup.

---

_Last updated: June 21, 2025_
