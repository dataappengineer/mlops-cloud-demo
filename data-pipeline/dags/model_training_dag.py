"""
Airflow DAG: model_training_pipeline

This DAG trains a scikit-learn model on validated data and uploads the trained model artifact to S3.
"""

from airflow import DAG
from airflow.utils.dates import days_ago
from datetime import timedelta
from airflow.operators.python import PythonOperator
import os
import pandas as pd
import joblib
import boto3
from botocore.exceptions import NoCredentialsError
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

def train_model(**context):
    # Path to validated data (produced by data_ingestion_dag)
    validated_path = context['params'].get('validated_path', '/opt/airflow/data/fetched_data_validated.csv')
    model_output_path = context['params'].get('model_output_path', '/opt/airflow/data/model.joblib')
    s3_bucket = context['params'].get('s3_bucket', 'mlops-processed-data-982248023588')
    s3_key = os.path.basename(model_output_path)

    print(f"[train_model] Loading data from {validated_path}")
    
    # Try different delimiters to handle various CSV formats
    try:
        df = pd.read_csv(validated_path, sep=';')
        print("[train_model] Successfully read semicolon-delimited file.")
    except:
        try:
            df = pd.read_csv(validated_path)
            print("[train_model] Successfully read comma-delimited file.")
        except Exception as e:
            print(f"[train_model] Error reading CSV: {e}")
            raise
    
    print(f"[train_model] Dataset shape: {df.shape}")
    print(f"[train_model] Column names: {list(df.columns)}")
    print(f"[train_model] Data types:\n{df.dtypes}")
    
    # Ensure we have valid data
    if df.empty:
        raise ValueError("Dataset is empty!")
    
    if len(df.columns) < 2:
        raise ValueError(f"Dataset must have at least 2 columns, got {len(df.columns)}")
    
    # Example: Assume last column is target
    X = df.iloc[:, :-1]
    y = df.iloc[:, -1]
    
    print(f"[train_model] Features shape: {X.shape}")
    print(f"[train_model] Target shape: {y.shape}")
    print(f"[train_model] Target unique values: {sorted(y.unique())}")
    
    # Ensure all features are numeric
    if not all(X.dtypes.apply(lambda x: x.kind in 'biufc')):
        print("[train_model] Warning: Non-numeric features detected. Converting to numeric.")
        X = X.apply(pd.to_numeric, errors='coerce')
        X = X.fillna(X.mean())  # Fill NaN with mean
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"[train_model] Model accuracy: {acc:.4f}")

    joblib.dump(clf, model_output_path)
    print(f"[train_model] Model saved to {model_output_path}")

    # Upload model to S3
    s3 = boto3.client('s3')
    try:
        s3.upload_file(model_output_path, s3_bucket, s3_key)
        print(f"[train_model] Model uploaded to s3://{s3_bucket}/{s3_key}")
    except NoCredentialsError:
        print("[train_model] S3 upload failed: No AWS credentials found.")
    except Exception as e:
        print(f"[train_model] S3 upload failed: {e}")

with DAG(
    dag_id='model_training_pipeline',
    default_args={
        'owner': 'airflow',
        'depends_on_past': False,
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    },
    description='Train a scikit-learn model and upload artifact to S3',
    schedule_interval=None,
    start_date=days_ago(1),
    catchup=False,
    tags=['mlops', 'model-training'],
    is_paused_upon_creation=False,
) as dag:
    train_model_task = PythonOperator(
        task_id='train_model',
        python_callable=train_model,
        provide_context=True,
        params={
            'validated_path': '/opt/airflow/data/fetched_data_validated.csv',
            'model_output_path': '/opt/airflow/data/model.joblib',
            's3_bucket': 'mlops-processed-data-982248023588',
        },
    )
