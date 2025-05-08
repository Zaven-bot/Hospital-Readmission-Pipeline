#!/bin/bash

# Initialize Airflow DB
until pg_isready -h postgres -p 5432 -U airflow; do
  echo "Waiting for Postgres..."
  sleep 2
done

# Retry advisory lock for DB migration (up to 5 times)
attempts=0
until airflow db init || [ $attempts -eq 5 ]; do
  echo "Database migration failed due to lock. Retrying... ($attempts)"
  attempts=$((attempts + 1))
  sleep 5
done

# Only create user if it doesn't exist
if ! airflow users list | grep -q admin; then
    echo "Creating admin user..."
    airflow users create \
        --username admin \
        --firstname airflow \
        --lastname admin \
        --role Admin \
        --email admin@example.com \
        --password admin
else
    echo "Admin user already exists, skipping creation."
fi

# Start scheduler in background
airflow scheduler &

# Start webserver
exec airflow webserver
