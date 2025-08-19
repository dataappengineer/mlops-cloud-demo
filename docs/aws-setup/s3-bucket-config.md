# S3 Bucket Configuration for MLOps Processed Data

>This document describes the configuration, usage, and best practices for the S3 bucket used to store processed data outputs from the MLOps pipeline.

---

## Bucket Overview
- **Name:** `mlops-processed-data-982248023588`
- **Region:** `us-east-1`
- **Purpose:** Store cleaned and processed CSV data, validation reports, and ML-ready datasets from Airflow DAGs.
- **Created By:** AWS CLI (profile: `mlops-dev-user`)

## Configuration Details
- **Versioning:** Enabled (tracks all object versions, supports rollback and data lineage)
- **Access:** Private (least privilege, no public access)
- **Storage Class:** Standard
- **IAM Access:** Only accessible via `mlops-dev-user` credentials/profile

## Usage Scenarios
This bucket is used for:
- Storing cleaned CSV files from raw data sources
- Uploading processed datasets for ML model training
- Saving data validation and profiling reports
- Maintaining historical versions for reproducibility and audit

## Creation & Management Steps
1. **Verify AWS Connection**
  ```sh
  aws sts get-caller-identity --profile mlops-dev-user
  ```
2. **Create the S3 Bucket**
  ```sh
  aws s3 mb s3://mlops-processed-data-982248023588 --region us-east-1 --profile mlops-dev-user
  ```
3. **Enable Versioning**
  ```sh
  aws s3api put-bucket-versioning --bucket mlops-processed-data-982248023588 --versioning-configuration Status=Enabled --profile mlops-dev-user
  ```
4. **Verify Versioning**
  ```sh
  aws s3api get-bucket-versioning --bucket mlops-processed-data-982248023588 --profile mlops-dev-user
  # Output should include: { "Status": "Enabled" }
  ```

## Versioning: Benefits & Commands
**Benefits:**
- Track data changes over time
- Rollback to previous data versions
- Maintain data lineage for ML experiments
- Recover from accidental deletion or corruption

**Key Commands:**
```sh
# List bucket contents
aws s3 ls s3://mlops-processed-data-982248023588/ --profile mlops-dev-user

# Upload processed data
aws s3 cp processed_data.csv s3://mlops-processed-data-982248023588/ --profile mlops-dev-user

# List all object versions
aws s3api list-object-versions --bucket mlops-processed-data-982248023588 --profile mlops-dev-user

# List versions of a specific file
aws s3api list-object-versions --bucket mlops-processed-data-982248023588 --prefix processed_data.csv --profile mlops-dev-user
```

## Security & Best Practices
- Enforce least privilege: restrict access to only required IAM users/roles (e.g., `mlops-dev-user`)
- No public access: ensure Block Public Access is enabled
- Enable bucket versioning for data protection and audit
- Use bucket policies or IAM policies to control access
- (Optional) Set up lifecycle policies to manage storage costs by expiring old versions
- Regularly review access logs and permissions
- Keep this file updated with any changes to bucket configuration

## References
- [AWS S3 Versioning Documentation](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Versioning.html)
- [AWS CLI S3 Reference](https://docs.aws.amazon.com/cli/latest/reference/s3/index.html)

---
This bucket is now ready to receive processed data from the Airflow pipeline. For pipeline integration details, see the data pipeline documentation.
