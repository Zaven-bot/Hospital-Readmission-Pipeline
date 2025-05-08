# 🧭 Project Repository Overview

This document summarizes the structure and responsibilities of the `readmission-pipeline-ml/` repository.

---

## 📁 Repository Structure

```
readmission-pipeline-ml/
├── airflow/                      # Airflow container files and DAGs
│   ├── dags/
│   │   └── readmission_dag.py    # Airflow DAG orchestrating ML pipeline
│   ├── Dockerfile                # Airflow Docker build
│   ├── init.sh                   # Script to initialize Airflow DB and services
│   └── requirements.txt          # Airflow Python dependencies
│
├── ml-pipeline/                 # ML container files
│   ├── Dockerfile                # ML pipeline Docker build
│   └── requirements.txt          # ML pipeline Python dependencies
│
├── scripts/                     # Source ML pipeline scripts
│   ├── clean.py                  # Clean raw data
│   ├── feature_engineering.py   # Feature transformation logic
│   ├── train_model.py           # Train a model and log to MLflow
│   ├── evaluate_model.py        # Evaluate model and log metrics
│   ├── ingest.py                # Data ingestion logic
│   ├── drop_column.py           # Utility script for feature dropping
│   └── pipeline.py              # Optional: complete pipeline runner
│
├── data/                        # Datasets
│   ├── raw/                      # Raw input data
│   └── processed/                # Cleaned and feature-engineered data
│       └── *.dvc                 # DVC tracking files
│
├── mlruns/                      # MLflow tracking directory
│   └── ...                       # Logs, metrics, artifacts, models
│
├── notebooks/                  # Jupyter notebooks for exploration
│   ├── 01_eda.ipynb             # Exploratory Data Analysis
│   └── 02_cleaning.ipynb        # Cleaning prototyping
│
├── models/                      # Optional: local saved models
│
├── .dvc/                        # DVC internal state
├── .git/                        # Git version control
├── docker-compose.yml           # Compose file to run containers
├── Makefile                     # Utility commands (legacy/manual)
├── env.yml                      # Old Conda environment (may be deprecated)
├── requirements-af.txt          # Airflow environment dependencies
├── requirements-ml.txt          # ML environment dependencies
├── confusion_matrix.png         # Evaluation output
├── roc_curve.png                # Evaluation output
├── last_run_id.txt              # Possibly stores MLflow run ID
├── README.md                    # Project README
└── repository_layout.txt        # Notes on layout
```

---

## 🔍 Component Responsibilities

### 🧠 ML Scripts (`scripts/`)

* **clean.py**: Cleans raw hospital data.
* **feature\_engineering.py**: Builds features used by model.
* **train\_model.py**: Trains a model, logs it to MLflow.
* **evaluate\_model.py**: Evaluates model and logs confusion matrix and scores.

### ⚙️ Workflow Automation

* **readmission\_dag.py**: Defines Airflow DAG with BashOperator to trigger each ML stage in its Docker container.
* **init.sh**: Handles `airflow db init` and service start logic with retries.
* **docker-compose.yml**: Spins up PostgreSQL, Airflow, and ML pipeline containers.

### 📦 Versioning & Tracking

* **MLflow (`mlruns/`)**: Logs metrics, models, and run metadata.
* **DVC (`data/processed/*.dvc`)**: Tracks data versions.

### 📊 Notebooks

* Used to develop, clean, and explore data prior to scripting pipeline logic.

---

Let me know if you'd like to split this into separate markdown files or automatically update your `README.md` with summarized content!
