# Data Ingestion Pipeline: Orchestration & Event-Driven Triggering

This pipeline demonstrates modern orchestration best practices using Apache Airflow. It supports both scheduled and event-driven (API) triggering, making it ideal for production and portfolio use.

---

## Features
- **Scheduled Execution:** Runs automatically on a daily schedule (configurable in the DAG).
- **Event-Driven/API Trigger:** Can be triggered externally via the Airflow REST API, simulating real-world event-driven workflows.
- **Parameterization:** Accepts custom parameters (e.g., CSV URL, output path) at runtime.

---

## How to Trigger the DAG

### 1. Scheduled (Automatic)
- The DAG runs daily by default. You can adjust the schedule in the DAG definition (`schedule_interval`).

### 2. Event-Driven (API) Trigger

You can trigger the DAG from any system using the Airflow REST API. This is production-relevant and great for portfolio demos.

#### **A. Using curl (Linux/macOS/Windows with Git Bash or WSL):**
```sh
curl -X POST "http://localhost:8080/api/v1/dags/data_ingestion_pipeline/dagRuns" \
  -H "Content-Type: application/json" \
  --user "admin:admin" \
  -d '{"conf": {"csv_url": "https://people.sc.fsu.edu/~jburkardt/data/csv/hw_200.csv", "output_path": "/opt/airflow/data/netflix_movies.csv"}}'
```

#### **B. Using PowerShell (Windows):**
```powershell
$headers = @{
  "Content-Type" = "application/json"
  "Authorization" = "Basic " + [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("admin:admin"))
}
$body = '{"conf": {"csv_url": "https://people.sc.fsu.edu/~jburkardt/data/csv/hw_200.csv", "output_path": "/opt/airflow/data/netflix_movies.csv"}}'
Invoke-RestMethod -Uri "http://localhost:8080/api/v1/dags/data_ingestion_pipeline/dagRuns" -Method Post -Headers $headers -Body $body
```

#### **C. Using Python:**
```python
import requests
from requests.auth import HTTPBasicAuth

url = "http://localhost:8080/api/v1/dags/data_ingestion_pipeline/dagRuns"
data = {
    "conf": {
        "csv_url": "https://people.sc.fsu.edu/~jburkardt/data/csv/hw_200.csv",
        "output_path": "/opt/airflow/data/netflix_movies.csv"
    }
}
resp = requests.post(url, json=data, auth=HTTPBasicAuth('admin', 'admin'))
print(resp.json())
```

---

## Optional: FileSensor for Local Event-Driven Demo
You can add a FileSensor to your DAG to wait for a file to appear in a directory, simulating event-driven orchestration without cloud dependencies.

---

## Portfolio/Production Best Practices
- **Show both scheduled and API triggers in your demo.**
- **Document the API trigger in your README (as above).**
- **(Optional) Add a FileSensor for local event-driven orchestration.**
- **No need to set up S3 unless you want to demo cloud integration.**

---

## Summary
- This pipeline is ready for both scheduled and event-driven (API) orchestration.
- The REST API trigger is the most universal and production-relevant demo.
- You can extend the pipeline with sensors or cloud integrations as needed.
