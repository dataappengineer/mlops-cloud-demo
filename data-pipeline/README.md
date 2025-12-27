# Data Pipeline - Airflow

This directory contains the Airflow-based data ingestion and processing pipeline.

## Quick Start

1. **Set up AWS credentials:**
   ```bash
   cp .env.example .env
   # Edit .env with your AWS credentials
   ```

2. **Build the custom Airflow image:**
   ```bash
   docker build -t mlops-airflow:custom-2.8.1 .
   ```

3. **Start Airflow:**
   ```bash
   docker-compose up -d
   ```

4. **Access Airflow UI:**
   - URL: http://localhost:8080
   - Username: `admin`
   - Password: `admin`

## Project Structure

```
data-pipeline/
├── Dockerfile              # Custom Airflow image with dependencies
├── docker-compose.yml      # Multi-container Airflow setup
├── requirements.txt        # Python packages for DAGs
├── .env.example           # Template for AWS credentials
├── dags/                  # Airflow DAG definitions
│   ├── data_ingestion_dag.py
│   └── model_training_dag.py
└── data/                  # Local data directory (gitignored)
```

## DAGs

### `data_ingestion_dag`
- Fetches CSV data from external sources
- Cleans and validates data
- Uploads processed data to S3

### `model_training_dag`
- Loads processed data from S3
- Trains ML model
- Saves model artifacts to S3

## AWS Integration

Requires:
- S3 bucket: `mlops-processed-data-982248023588`
- AWS credentials with S3 access
- Region: `us-east-1`

See `../docs/aws-setup/` for detailed configuration.

## Troubleshooting

**Containers not starting?**
- Check AWS credentials in `.env`
- Ensure Docker daemon is running
- Check logs: `docker-compose logs`

**DAGs not appearing?**
- Wait 30 seconds for scheduler to pick up changes
- Check DAG syntax: `docker-compose exec airflow-scheduler airflow dags list`

**Port 8080 already in use?**
- Change port in `docker-compose.yml`: `"8081:8080"`
