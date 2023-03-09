from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash_operator import BashOperator

default_args = {
    'owner': 'backup_user',
    'depends_on_past': False,
    'start_date': datetime(2023, 3, 6),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'backup_dag',
    default_args=default_args,
    description='A DAG to perform backup task',
    schedule_interval=timedelta(days=1),
)

backup_script = BashOperator(
    task_id='backup_script',
    bash_command='python /var/backup_ILRI/DAG_adgg/backup.py',
    dag=dag,
)