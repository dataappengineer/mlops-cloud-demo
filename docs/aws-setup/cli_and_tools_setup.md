# AWS CLI and Tools Setup

## Configure AWS CLI with IAM User Credentials
1. Install the AWS CLI: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
2. Run `aws configure` and enter your IAM user's Access Key ID, Secret Access Key, default region (e.g., us-east-1), and output format (e.g., json).
3. Verify setup with `aws sts get-caller-identity`.

## Setting Up VS Code for AWS
- Install the "AWS Toolkit for Visual Studio Code" extension.
- Connect the extension to your AWS account using your IAM credentials/profile.

## Setting Up Terraform for AWS
- Install Terraform: https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli
- Use the AWS CLI profile or set environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION`).
- Example provider block in Terraform:
  ```hcl
  provider "aws" {
    region = "us-east-1"
    profile = "default"
  }
  ```

## Setting Up GitHub Actions for AWS
- Store your IAM user's access keys as GitHub repository secrets (e.g., `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`).
- Use the `aws-actions/configure-aws-credentials` action in your workflow:
  ```yaml
  - uses: aws-actions/configure-aws-credentials@v4
    with:
      aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
      aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
      aws-region: us-east-1
  ```

# Verifying Your AWS CLI Profile and Access

After configuring your AWS CLI profile, you can verify that it is set up correctly and has access to your AWS account by running the following command in your terminal:

```powershell
aws sts get-caller-identity
```

A successful response will look like this (with generic values):

```
{
    "UserId": "AIDAEXAMPLEUSERID",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/user-with-least-privileges"
}
```

- If you see your user and account information, your profile is set up and working.
- If you get an error, check your credentials and permissions.

You can also use this command to confirm which profile is active and which user is being used for AWS CLI operations.
