FROM apache/airflow:latest

USER root

# Install system dependencies
#RUN apt-get update && \
    #apt-get -y install git && \
    #apt-get clean


RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    git \
    wget \
    unzip \
    libnss3 \
    libgconf-2-4 \
    fonts-liberation \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxi6 \
    libxtst6 \
    libxrandr2 \
    xdg-utils \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libxss1 \
    && apt-get clean

# Switch to airflow user
USER airflow

# Copy requirements
COPY AIRFLOW/dags/requirements.txt /tmp/requirements.txt
RUN ls -l /tmp/requirements.txt
RUN cat /tmp/requirements.txt

# Install Python packages
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r /tmp/requirements.txt