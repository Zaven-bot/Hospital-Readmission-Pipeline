
# Hospital Readmission Pipeline (ML + Airflow)

This project implements a complete machine learning pipeline for predicting hospital readmissions. It uses Apache Airflow to orchestrate tasks, MLflow to track model training, Docker for environment isolation, and DVC for data versioning.

---

## Project Summary

- **ML Tasks**: Data ingestion, cleaning, feature engineering, training, evaluation.
- **Orchestration**: Airflow DAG uses `BashOperator` to run each step in the ML pipeline.
- **Tracking**: MLflow logs metrics, parameters, and artifacts.
- **Versioning**: DVC tracks raw and processed datasets.
- **Environment Isolation**: Two Docker containers (`airflow`, `ml-pipeline`).
- **Service Management**: Docker Compose launches the full stack.

---

## Repository Layout

```
readmission-pipeline-ml/
├── airflow/
│   ├── dags/
│   │   └── readmission_dag.py         # DAG defining ML pipeline orchestration
│   ├── Dockerfile                     # Airflow service container
│   ├── init.sh                        # DB init & graceful handling script
│   └── requirements.txt               # Python dependencies for Airflow
│
├── ml-pipeline/
│   ├── Dockerfile                     # ML pipeline container
│   └── requirements.txt               # Python dependencies for ML tasks
│
├── scripts/                           # Modular ML pipeline components
│   ├── ingest.py
│   ├── clean.py
│   ├── drop_column.py
│   ├── feature_engineering.py
│   ├── train_model.py
│   ├── evaluate_model.py
│   └── pipeline.py                    # (Optional) End-to-end runner
│
├── data/
│   ├── raw/
│   │   └── hospital_readmissions.csv  # Raw source data
│   └── processed/
│       ├── cleaned_data.csv
│       ├── featured_data.csv
│       ├── test_data.pkl
│       └── *.dvc                      # DVC tracking files
│
├── mlruns/                            # MLflow experiment logs & model registry
│   ├── 0/, ...                        # Individual run folders
│   └── models/ReadmissionModel/...   # Model versions and metadata
│
├── notebooks/
│   ├── 01_eda.ipynb                   # Exploratory Data Analysis
│   └── 02_cleaning.ipynb              # Cleaning prototyping
│
├── models/                            # (Optional) Local model storage
├── docker-compose.yml                 # Defines all services
├── Makefile                           # Manual build/run commands (optional)
├── env.yml                            # Old Conda environment spec
├── last_run_id.txt                    # Stores last MLflow run ID
├── confusion_matrix.png               # Evaluation artifact
├── roc_curve.png                      # Evaluation artifact
└── README.md                          # You are here!
```

---

## 🧠 ML Pipeline Steps

Each ML step is executed in a Dockerized script:

1. **Ingest** → `scripts/ingest.py`
2. **Clean** → `scripts/clean.py`
3. **Feature Engineering** → `scripts/feature_engineering.py`
4. **Train Model** → `scripts/train_model.py`
5. **Evaluate** → `scripts/evaluate_model.py`

Artifacts and metrics are logged to MLflow.

---

## ⚙️ Architecture Overview

```
┌────────────────────────────────────────────────────────────────────────────┐
│                             🧠 User (You)                                   │
│   Runs: `docker compose up --build` to launch the full ML system stack     │
└────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌──────────────────────────── Docker Compose Stack ───────-────────────────────┐
│                                                                              │
│  ┌────────────────────────────┐          ┌──────────────────────────────┐    │
│  │     Airflow Container      │          │      ML Pipeline Container   │    │
│  │  - Airflow Webserver (UI)  │◄──┐      │  - Python 3.10, scikit-learn │    │
│  │  - Airflow Scheduler       │   │      │  - Runs ML scripts           │    │
│  └────────────┬───────────────┘   │      └──────────────┬───────────────┘    │
│               │                   │                     │                    │
│               ▼                   │                     ▼                    │
│     ┌───────────────────────┐     │       ┌──────────────────────────────┐   │
│     │ DAG: readmission_dag  │─────┘       │   Scripts: clean, feature,   │   │
│     │ BashOperators (steps) │────────────▶│   train, evaluate (Python)   │   │
│     └───────────────────────┘             └──────────────────────────────┘   │
│               │                                                    ▲         │
│               ▼                                                    │         │
│   ┌────────────────────────────┐           ┌────────────────────┐  │         │
│   │    PostgreSQL Container    │◄──────────┤   Airflow Metadata │  │         │
│   │ - Stores DAG/task state    │           └────────────────────┘  │         │
│   └────────────────────────────┘                                   │         │
│                                                                    │         │
│                   Logs metrics and artifacts using                 │         │
│                   MLflow Tracking Server (inside container)  ◄─────┘         │
│                         - model.pkl                                │         │
│                         - metrics.json                             │         │
│                         - confusion_matrix.png                     │         │
└──────────────────────────────────────────────────────────────────────────────┘

        ▼                                                                  ▲
        ▼──────────────────────────────────────────────────────────────────┘
        ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                    🧬 Data Version Control (DVC) & Local Files             │
│                                                                            │
│  - Data files like cleaned_data.csv and test_data.pkl are DVC-tracked      │
│  - Stored **outside** Git to avoid large file issues                       │
│  - Only metadata `.dvc` files are committed to Git                         │
│  - Actual data lives in your local filesystem or DVC remote                │
└────────────────────────────────────────────────────────────────────────────┘

```


---

## 🧪 Local Development

```bash
# Stop & reset containers
docker compose down -v

# Rebuild everything
docker compose build

# Launch stack
docker compose up
```

---

## Next Steps

- Trigger DAG and run full pipeline from Airflow UI
- View metrics & artifacts in MLflow UI
- Add FASTAPI or Streamlit frontend
- (Future) Deploy to the cloud
