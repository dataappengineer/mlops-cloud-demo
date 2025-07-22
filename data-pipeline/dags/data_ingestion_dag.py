"""
Airflow DAG: data_ingestion_pipeline

This DAG orchestrates a data ingestion pipeline with the following steps:
- Fetch a CSV file from an external source (public URL or predefined location)
- (To be added) Clean/process the data
- (To be added) Upload the processed data to S3

Author: Giovanni Brucoli
Date: 2025-06-25

Usage:
- Place this file in the data-pipeline/dags/ directory of your Airflow project.
- The DAG runs daily and can be triggered manually for testing.
- The fetch_csv task downloads a CSV and saves it to /tmp/fetched_data.csv by default.
- Parameters can be customized in the PythonOperator params.

Next steps:
- Implement data cleaning and S3 upload tasks.
"""

from airflow import DAG
from airflow.utils.dates import days_ago
from datetime import timedelta

from airflow.operators.python import PythonOperator
import requests
import os
import pandas as pd
import boto3
from botocore.exceptions import NoCredentialsError

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}


def fetch_csv(**context):
    url = context['params'].get('csv_url', 'https://people.sc.fsu.edu/~jburkardt/data/csv/airtravel.csv')
    output_path = context['params'].get('output_path', '/opt/airflow/data/fetched_data.csv')
    response = requests.get(url)
    response.raise_for_status()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'wb') as f:
        f.write(response.content)
    print(f"CSV downloaded to {output_path}")
    # Push the path to XCom for downstream tasks
    context['ti'].xcom_push(key='csv_path', value=output_path)

def clean_csv(**context):
    ti = context['ti']
    input_path = ti.xcom_pull(key='csv_path', task_ids='fetch_csv')
    cleaned_path = input_path.replace('.csv', '_cleaned.csv')
    print(f"Cleaning CSV: {input_path} -> {cleaned_path}")
    df = pd.read_csv(input_path)
    # Example cleaning: drop rows with any missing values
    df_cleaned = df.dropna()
    df_cleaned.to_csv(cleaned_path, index=False)
    print(f"Cleaned CSV saved to {cleaned_path}")
    ti.xcom_push(key='cleaned_csv_path', value=cleaned_path)

def upload_to_s3(**context):
    ti = context['ti']
    cleaned_path = ti.xcom_pull(key='cleaned_csv_path', task_ids='clean_csv')
    s3_bucket = context['params'].get('s3_bucket', 'your-s3-bucket-name')
    s3_key = os.path.basename(cleaned_path)
    print(f"Uploading {cleaned_path} to s3://{s3_bucket}/{s3_key}")
    s3 = boto3.client('s3')
    try:
        s3.upload_file(cleaned_path, s3_bucket, s3_key)
        print(f"Upload successful: s3://{s3_bucket}/{s3_key}")
    except NoCredentialsError:
        print("S3 upload failed: No AWS credentials found.")
    except Exception as e:
        print(f"S3 upload failed: {e}")

with DAG(
    dag_id='data_ingestion_pipeline',
    default_args=default_args,
    description='Orchestrates data ingestion, cleaning, and upload to S3',
    schedule_interval='@daily',
    start_date=days_ago(1),
    catchup=False,
    tags=['mlops', 'data-ingestion'],
    is_paused_upon_creation=False,
) as dag:
    fetch_csv_task = PythonOperator(
        task_id='fetch_csv',
        python_callable=fetch_csv,
        provide_context=True,
        params={
            'csv_url': 'https://people.sc.fsu.edu/~jburkardt/data/csv/airtravel.csv',
            'output_path': '/opt/airflow/data/fetched_data.csv',
        },
    )

    clean_csv_task = PythonOperator(
        task_id='clean_csv',
        python_callable=clean_csv,
        provide_context=True,
    )

    upload_to_s3_task = PythonOperator(
        task_id='upload_to_s3',
        python_callable=upload_to_s3,
        provide_context=True,
        params={
            's3_bucket': 'your-s3-bucket-name',  # <-- Replace with your actual S3 bucket
        },
    )

    fetch_csv_task >> clean_csv_task >> upload_to_s3_task
