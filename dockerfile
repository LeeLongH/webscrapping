FROM apache/airflow:latest

USER root

# Install system dependencies
RUN apt-get update && \
    apt-get -y install git && \
    apt-get clean

# Switch to airflow user
USER airflow

# Copy requirements into container
COPY requirements.txt /tmp/requirements.txt

# Install packages into Airflow's virtualenv
RUN pip install --no-cache-dir -r /tmp/requirements.txt