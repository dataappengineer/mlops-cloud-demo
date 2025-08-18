"""
Airflow DAG: data_ingestion_pipeline

This DAG orchestrates a data ingestion pipeline with the following steps:
- Fetch a CSV file from an external source (public URL or predefined location)
- (To be added) Clean/process the data
- (To be added) Upload the processed data to S3

Author: Giovanni Brucoli
Date: 2025-08-18

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
import janitor  # pyjanitor for advanced cleaning

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
    print(f"[clean_csv] Cleaning CSV: {input_path} -> {cleaned_path}")
    df = pd.read_csv(input_path)

    # 1. Standardize column names
    df = df.clean_names()  # pyjanitor: snake_case, lowercase
    print("[clean_csv] Standardized column names.")

    # 2. Drop duplicates
    before = len(df)
    df = df.drop_duplicates()
    print(f"[clean_csv] Dropped duplicates: {before - len(df)} rows removed.")


    # 3. Analyze missing data mechanism and impute
    na_total = df.isna().sum().sum()
    print(f"[clean_csv] Total missing values before imputation: {na_total}")
    if na_total > 0:
        # MCAR/MAR/NMAR hint (simple heuristic)
        na_cols = df.isna().sum()
        if (na_cols == na_cols.iloc[0]).all():
            print("[clean_csv] Missingness appears uniform across columns (possible MCAR).")
        elif any(df.isna().sum() > 0):
            print("[clean_csv] Missingness may depend on observed data (possible MAR or NMAR). Review domain knowledge.")

        # Impute numeric columns with mean
        num_cols = df.select_dtypes(include='number').columns
        for col in num_cols:
            if df[col].isna().any():
                mean_val = df[col].mean()
                df[col] = df[col].fillna(mean_val)
                print(f"[clean_csv] Imputed numeric column '{col}' with mean: {mean_val}")

        # Impute categorical columns with mode
        cat_cols = df.select_dtypes(include='object').columns
        for col in cat_cols:
            if df[col].isna().any():
                mode_val = df[col].mode().iloc[0] if not df[col].mode().empty else ''
                df[col] = df[col].fillna(mode_val)
                print(f"[clean_csv] Imputed categorical column '{col}' with mode: {mode_val}")

        # Optional: KNN imputation if pyjanitor/sklearn is available (advanced)
        try:
            from sklearn.impute import KNNImputer
            imputer = KNNImputer(n_neighbors=3)
            df[num_cols] = imputer.fit_transform(df[num_cols])
            print("[clean_csv] Applied KNN imputation to numeric columns.")
        except ImportError:
            print("[clean_csv] sklearn not available, skipping KNN imputation.")

        na_after = df.isna().sum().sum()
        print(f"[clean_csv] Total missing values after imputation: {na_after}")
        if na_after > 0:
            print(f"[clean_csv] {na_after} missing values remain after imputation. Dropping remaining rows with NA.")
            df = df.dropna()

    # 4. Trim strings and convert types (example: try to parse dates)
    for col in df.select_dtypes(include='object').columns:
        df[col] = df[col].astype(str).str.strip()
    print("[clean_csv] Trimmed whitespace from string columns.")

    # 5. (Optional) Convert date columns if present
    for col in df.columns:
        if 'date' in col:
            try:
                df[col] = pd.to_datetime(df[col], errors='coerce')
                print(f"[clean_csv] Converted {col} to datetime.")
            except Exception:
                pass

    # 6. Save cleaned file
    df.to_csv(cleaned_path, index=False)
    print(f"[clean_csv] Cleaned CSV saved to {cleaned_path}")
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
