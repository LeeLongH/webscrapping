from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.email import EmailOperator
from airflow.utils.trigger_rule import TriggerRule

from datetime import datetime, timedelta

from webscrapping import run_webscrapping
from format_mail import compose_email

default_args = {
    'start_date': datetime.now() - timedelta(days=1),
    'email_on_failure': True,
    'email_on_retry': False,
    'email': ['leon.sturm2@.com'],
    'retries': 1,
    'retry_delay': timedelta(minutes=5)
}

dag = DAG(
    'Job_Scrapping',
    default_args=default_args,
    schedule=None,
    catchup=False
)

    # --- WEBSCRAPPING ---
call_webscrapping = PythonOperator(
    task_id = 'webscrapping.py',
    python_callable = run_webscrapping,
    dag=dag
)

    # --- MAIL ---
send_email = PythonOperator(
    task_id='send_email',
    python_callable=compose_email,
    trigger_rule='all_done',    
    dag=dag
)

call_webscrapping >> send_email