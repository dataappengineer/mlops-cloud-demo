# Dockerfile for custom Airflow image with extra Python packages
FROM apache/airflow:2.8.1

# Copy requirements.txt into the image
COPY requirements.txt /requirements.txt

# Install extra Python packages
RUN pip install --no-cache-dir -r /requirements.txt

# Optionally, set a label to indicate customization
LABEL maintainer="dataappengineer" \
      description="Custom Airflow image with additional Python packages for MLOps pipeline"
