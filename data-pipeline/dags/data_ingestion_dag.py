def validate_data(**context):
    """
    Data validation task: detects and removes outliers using Z-score and IQR methods.
    Logs the number of outliers removed for each numeric column.
    """
    import numpy as np
    ti = context['ti']
    cleaned_path = ti.xcom_pull(key='cleaned_csv_path', task_ids='clean_csv')
    validated_path = cleaned_path.replace('_cleaned.csv', '_validated.csv')
    print(f"[validate_data] Validating data: {cleaned_path} -> {validated_path}")
    df = pd.read_csv(cleaned_path)

    num_cols = df.select_dtypes(include='number').columns
    for col in num_cols:
        # Z-score method
        z_scores = np.abs((df[col] - df[col].mean()) / df[col].std(ddof=0))
        z_outliers = z_scores > 3
        # IQR method
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        iqr_outliers = (df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))
        # Combine both
        outliers = z_outliers | iqr_outliers
        n_outliers = outliers.sum()
        if n_outliers > 0:
            print(f"[validate_data] {n_outliers} outliers detected in column '{col}' (removed).")
            df = df[~outliers]

    df.to_csv(validated_path, index=False)
    print(f"[validate_data] Validated data saved to {validated_path}")
    ti.xcom_push(key='validated_csv_path', value=validated_path)
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
    """
    Advanced, portfolio-grade data cleaning function.
    - Standardizes column names, drops duplicates, trims strings, parses dates.
    - Handles missing data with imputation (mean, mode, KNN if available) and only drops rows as a last resort.
    - Analyzes missing data mechanisms:
        * MCAR: Missing Completely At Random (missingness is unrelated to data)
        * MAR: Missing At Random (missingness related to observed data)
        * NMAR: Not Missing At Random (missingness related to unobserved/missing data)
    - Logs each step for transparency and extensibility.
    """
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


        num_cols = df.select_dtypes(include='number').columns
        used_knn = False
        # Try KNN imputation for numeric columns if sklearn is available
        try:
            from sklearn.impute import KNNImputer
            if df[num_cols].isna().sum().sum() > 0:
                imputer = KNNImputer(n_neighbors=3)
                df[num_cols] = imputer.fit_transform(df[num_cols])
                print("[clean_csv] Applied KNN imputation to numeric columns.")
                used_knn = True
        except ImportError:
            print("[clean_csv] sklearn not available, skipping KNN imputation.")

        # If KNN not used, fallback to mean imputation for numeric columns
        if not used_knn:
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

    validate_data_task = PythonOperator(
        task_id='validate_data',
        python_callable=validate_data,
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

    fetch_csv_task >> clean_csv_task >> validate_data_task >> upload_to_s3_task
