FROM apache/airflow:latest

USER root

# Install system dependencies
RUN apt-get update && \
    apt-get -y install git && \
    apt-get clean
    
# Install Python packages required by your DAGs
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

USER airflow