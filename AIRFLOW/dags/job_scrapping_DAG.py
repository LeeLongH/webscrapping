from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

from datetime import datetime

from webscrapping import run_webscrapping

default_args = {
    'start_date': datetime.now() - timedelta(days=1)
}

dag = DAG(
    'Job_Scrapping',
    default_args=default_args,
    schedule='0 18 * * *',
    catchup=False
)

# Print DAG started
start_msg = PythonOperator(
    task_id = 'webscrapping.py',
    python_callable = lambda: print('DAG started!'),
    dag=dag
)

# proceede with webscrapping
call_webscrapping= PythonOperator(
    task_id = 'webscrapping.py',
    python_callable = run_webscrapping,
    dag=dag
)

# Print DAG finished
finish_msg = PythonOperator(
    task_id = 'webscrapping.py',
    python_callable = lambda: print('DAG finished!'),
    dag=dag
)

start_msg >> call_webscrapping >> finish_msg