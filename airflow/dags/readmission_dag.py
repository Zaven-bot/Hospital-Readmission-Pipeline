from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.models import Variable

# Configurable Airflow Variables
RUN_GROUP = Variable.get("RUN_GROUP", default_var="default_run")

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
}

with DAG(
    dag_id='readmission_pipeline', # Identifier for DAG
    default_args=default_args,  #
    schedule_interval=None,
    catchup=False,
    tags=['mlops', 'readmission'],
) as dag:

    clean_task = BashOperator(
        task_id='clean_data',
        bash_command=(
            'docker exec ml-pipeline python scripts/clean.py '
            '--input data/raw/hospital_readmissions.csv'
            '--output data/processed/cleaned_data.csv'
        )
    )

    feature_task = BashOperator(
        task_id='feature_engineering',
        bash_command=(
            'docker exec ml-pipeline python scripts/feature_engineering.py '
            '--input data/processed/cleaned_data.csv '
            '--output data/processed/featured_data.csv'
        )
    )

    train_task = BashOperator(
        task_id='train_model',
        bash_command=(
            'docker exec ml-pipeline python scripts/train_model.py '
            '--input data/processed/featured_data.csv '
            '--run-group {{ params.run_group }}'
        ),
        params={'run_group': RUN_GROUP},
    )

    evaluate_task = BashOperator(
        task_id='evaluate_model',
        bash_command=(
            'docker exec ml-pipeline python scripts/evaluate_model.py '
            '--run-group {{ params.run_group }} '
            '--model-name ReadmissionModel '
            '--stage Staging'
        ),
        params={'run_group': RUN_GROUP},
    )

    clean_task >> feature_task >> train_task >> evaluate_task














# from datetime import datetime
# from airflow import DAG
# from airflow.operators.python import PythonOperator
# import sys
# import os

# # Ensure your scripts are importable
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../scripts')))

# from clean import main as clean_main
# from feature_engineering import main as feature_main
# from train_model import main as train_main
# from evaluate_model import main as evaluate_main

# def evaluate_with_run_id():
#     with open('last_run_id.txt', 'r') as f:
#         run_id = f.read().strip()
#     evaluate_main(run_id=run_id)

# def train_and_capture_run_id():
#     train_main()
#     # This assumes train_main() already saves run_id into last_run_id.txt

# with DAG(
#     dag_id='readmission_pipeline',
#     start_date=datetime(2023, 1, 1),
#     schedule_interval=None,  # You can change this to '@daily' or CRON
#     catchup=False,
#     tags=['mlops', 'readmission'],
# ) as dag:

#     clean_task = PythonOperator(
#         task_id='clean_data',
#         python_callable=clean_main
#     )

#     feature_task = PythonOperator(
#         task_id='feature_engineering',
#         python_callable=feature_main
#     )

#     train_task = PythonOperator(
#         task_id='train_model',
#         python_callable=train_and_capture_run_id
#     )

#     evaluate_task = PythonOperator(
#         task_id='evaluate_model',
#         python_callable=evaluate_with_run_id
#     )

#     clean_task >> feature_task >> train_task >> evaluate_task
