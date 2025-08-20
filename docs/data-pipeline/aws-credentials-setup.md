# Setting Up AWS Credentials for Airflow S3 Access

To enable your Airflow pipeline to upload data to S3, you must provide your AWS credentials to the Airflow containers. This is done by creating a `.env` file in your project root with your AWS credentials, which are then passed into the containers via `docker-compose.airflow.yaml`.

## Steps

1. **Obtain your AWS credentials**
   - If you use a named AWS CLI profile (e.g., `mlops-dev-user`), you can retrieve your credentials with:
     ```sh
     aws configure get aws_access_key_id --profile mlops-dev-user
     aws configure get aws_secret_access_key --profile mlops-dev-user
     ```

2. **Create a `.env` file in your project root**
   - Add the following lines, replacing the values with your actual credentials:
     ```env
     AWS_ACCESS_KEY_ID=your-access-key-id
     AWS_SECRET_ACCESS_KEY=your-secret-access-key
     ```
   - (Optional) You can also set `AWS_DEFAULT_REGION=us-east-1` if you want to override the default region.

3. **How it works**
   - The `docker-compose.airflow.yaml` file is configured to pass these environment variables into all Airflow containers. This allows Airflow tasks (such as S3 uploads) to authenticate with AWS.

4. **Security Note**
   - Your `.env` file is listed in `.gitignore` and should never be committed to version control.
   - Treat your credentials as sensitive information.

---

For more details, see the S3 bucket configuration documentation in `../aws-setup/s3-bucket-config.md`.
