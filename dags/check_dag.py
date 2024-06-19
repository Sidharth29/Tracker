from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator

from random import randint
from datetime import datetime




def _print_confirmation():
    lambda: print(open('/opt/airflow/output/dummy', 'rb').read())

with DAG(
    "check_dag",
    start_date=datetime(2024,5,1),
    schedule_interval='0 0 7 * *',
    description="Creates a file and checks creation, belongs to Data Engineering team",
    tags=["data_engineering"]
) as dag:
    create_file = BashOperator(
                               task_id="create_file",
                               bash_command='echo "Hi there!" >/opt/airflow//output/dummy'
                               )

    check_file = BashOperator(
                              task_id="check_file",
                              bash_command="test -f /opt/airflow/output/dummy"
                             )

    print_confirmation = PythonOperator(
                                        task_id="print_confirmation",
                                        python_callable=_print_confirmation
                                        )



create_file >> check_file >> print_confirmation