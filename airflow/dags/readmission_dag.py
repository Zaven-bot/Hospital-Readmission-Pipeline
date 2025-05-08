from datetime import datetime
from airflow import DAG
from airflow.operators.bash import BashOperator

with DAG(
    dag_id='readmission_pipeline',
    start_date=datetime(2023, 1, 1),
    schedule_interval=None,  # Change to '@daily' or CRON if needed
    catchup=False,
    tags=['mlops', 'readmission'],
) as dag:

    clean_task = BashOperator(
        task_id='clean_data',
        bash_command='docker exec ml-pipeline python scripts/clean.py'
    )

    feature_task = BashOperator(
        task_id='feature_engineering',
        bash_command='docker exec ml-pipeline python scripts/feature_engineering.py'
    )

    train_task = BashOperator(
        task_id='train_model',
        bash_command='docker exec ml-pipeline python scripts/train_model.py'
    )

    evaluate_task = BashOperator(
        task_id='evaluate_model',
        bash_command='docker exec ml-pipeline python scripts/evaluate_model.py'
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
