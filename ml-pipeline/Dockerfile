# Dockerfile for ML pipeline environment
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && apt-get clean

# Install ML dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
