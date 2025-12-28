# Infrastructure - Terraform

This directory contains Infrastructure as Code (IaC) configuration for deploying AWS resources.

## Setup

1. Install Terraform (v1.0+)
2. Copy `.env.example` to `.env` and configure credentials
3. Initialize: `terraform init`
4. Plan: `terraform plan`
5. Apply: `terraform apply`

## AWS Resources

- S3 buckets for data storage
- IAM roles and policies
- (Add more as infrastructure grows)

## Credentials

Never commit credentials! Use `.env` file (gitignored) or AWS profiles.

See `../docs/aws-setup/` for detailed AWS configuration instructions.
