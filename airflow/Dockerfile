# Dockerfile for Airflow environment
FROM apache/airflow:2.6.3-python3.10

USER root

# Install common tools
RUN apt-get update && apt-get install -y \
    git \
    nano \
    curl \
    && apt-get clean

USER airflow

# Copy requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy DAGs and init script
COPY ./dags /opt/airflow/dags
COPY ./init.sh /opt/airflow/init.sh

USER root
RUN chmod +x /opt/airflow/init.sh
USER airflow

ENTRYPOINT ["/opt/airflow/init.sh"]
