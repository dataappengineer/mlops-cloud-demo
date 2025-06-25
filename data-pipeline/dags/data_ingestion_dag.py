from airflow import DAG
from airflow.utils.dates import days_ago
from datetime import timedelta
from airflow.operators.python import PythonOperator
import requests
import os

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
    output_path = context['params'].get('output_path', '/tmp/fetched_data.csv')
    response = requests.get(url)
    response.raise_for_status()
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'wb') as f:
        f.write(response.content)
    print(f"CSV downloaded to {output_path}")
    # Optionally push the path to XCom for downstream tasks
    context['ti'].xcom_push(key='csv_path', value=output_path)

with DAG(
    dag_id='data_ingestion_pipeline',
    default_args=default_args,
    description='Orchestrates data ingestion, cleaning, and upload to S3',
    schedule_interval='@daily',
    start_date=days_ago(1),
    catchup=False,
    tags=['mlops', 'data-ingestion'],
) as dag:
    fetch_csv_task = PythonOperator(
        task_id='fetch_csv',
        python_callable=fetch_csv,
        provide_context=True,
        params={
            'csv_url': 'https://people.sc.fsu.edu/~jburkardt/data/csv/airtravel.csv',
            'output_path': '/tmp/fetched_data.csv',
        },
    )
    # Task definitions for cleaning and upload will be added next
