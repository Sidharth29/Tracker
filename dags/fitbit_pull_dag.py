from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.load_to_db import health_db
from src.fitbit import get_logged_runs
from src.utils import generate_date_list

from random import randint
from datetime import datetime, timedelta
import pandas as pd
import os
import requests
from airflow.utils.log.logging_mixin import LoggingMixin
import logging
import pendulum
import dotenv

dotenv.load_dotenv()

logger = LoggingMixin().log
logger.setLevel(logging.INFO)


access_token="eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIyM1JYRFIiLCJzdWIiOiI5V1QzQkgiLCJpc3MiOiJGaXRiaXQiLCJ0eXAiOiJhY2Nlc3NfdG9rZW4iLCJzY29wZXMiOiJyc29jIHJlY2cgcnNldCByb3h5IHJudXQgcnBybyByc2xlIHJjZiByYWN0IHJsb2MgcnJlcyByd2VpIHJociBydGVtIiwiZXhwIjoxNzQ2ODUyNjI0LCJpYXQiOjE3MTUzMTY5OTR9.xcJoIi_O8rYh-sVXUbc0bBOk1JYCuLzYhzB3hJ9Tx1c"


headers = {
            'Authorization': f'Bearer {access_token}'
        }

src_dir = os.path.dirname(os.path.abspath(__file__))
repo_dir = os.path.dirname(src_dir)
output_dir = os.path.join(repo_dir,'output')


def _get_heartrate():
    """
    Fetches the heart rate date till yesterday
    """

    # Latest date to fetch data - yesterday
    pt=pendulum.timezone('America/Los_Angeles')
    yesterday = datetime.now(pt) - timedelta(days=1)
    
    try:
        # Get latest date loaded into db
        max_date = health_db.get_latest_date(table_name='heartrate_daily', schema='heartrate_silver', date_field="date")
    except:
         max_date = yesterday - timedelta(days=1)
    
    # Date range to extract data
    date_range = generate_date_list(start_date=max_date, end_date=yesterday.date())

    for dt in date_range:
        dt_formatted = dt.strftime('%Y-%m-%d')

        url = f"https://api.fitbit.com/1/user/-/activities/heart/date/{dt_formatted}/1d/1min/time/00:00/23:59.json"

        response = requests.get(url, headers=headers)

        response_json = response.json()

        if response.status_code != 200:
            logger.error(f'API call failed with status: {response.status_code}')


        heartrate_data = response_json['activities-heart-intraday']['dataset']
            
        df_heartrate = pd.DataFrame(heartrate_data)

        df_heartrate['date'] = dt

        df_heartrate = df_heartrate.rename({'value':'heartrate'}, axis=1)

        df_heartrate = df_heartrate[['date','time','heartrate']]

        df_heartrate['data_insert_timestamp'] = datetime.now()

        logger.info(f"Successfully extracted data for {dt}: {df_heartrate.head()}")

        logger.info(f'Storing file {output_dir}/heartrate_{dt}.csv')

        df_heartrate.to_csv(f'/opt/airflow/output/heartrate_{dt}.csv',index=False, mode='w')


def _load_to_heartrate_db():
    """
    Loads the onboarded CSV data into the POSTGRES db
    """
    health_db.load_files_to_db(keyword="heartrate", table_name='heartrate_data', schema='heartrate')


def _load_runs_to_db():
    """
    Fetches the runs for the unupdated range and loads it to the DB
    """
    # Latest date to fetch data - yesterday
    pt=pendulum.timezone('America/Los_Angeles')
    yesterday = datetime.now(pt) - timedelta(days=1)

    yesterday = pd.to_datetime(yesterday.date())

    try:
        # Get latest date loaded into db
        max_date = health_db.get_latest_date(table_name='heartrate_daily', schema='heartrate_silver', date_field="date")
    except:
         # If the table does not exist - Scan prior 3 days for runs as default 
         max_date = yesterday - timedelta(days=3)

    max_date = pd.to_datetime(max_date)

    days_unpdated = pd.Timedelta(value=(yesterday - max_date), unit='days').days

    df_runs = get_logged_runs(n_days=days_unpdated+2)

    if df_runs is not None and not df_runs.empty:
        # Upload to Database
        health_db.load_df_to_db(df=df_runs, table_name='all_runs', schema='runs')
    else:
        logger.info(f'No logged runs between {max_date} - {yesterday}')
    

with DAG(
         "fitbit_data_pull", \
         default_args={
        'depends_on_past': False,
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
         },
         description='A DAG to pull Heartrate from Fitbit API and store as CSV',
         start_date=datetime(2024,5,11), \
         schedule_interval='0 18 * * *',
         catchup=False) as dag:
            

        get_heart_rate = PythonOperator(
            task_id = "get_heart_rate",
            python_callable = _get_heartrate
        )

        load_heart_rate = PythonOperator(
            task_id = "load_heart_rate",
            python_callable = _load_to_heartrate_db
        )

        get_and_load_runs = PythonOperator(
            task_id = "get_and_load_runs",
            python_callable = _load_runs_to_db
        )

        agg_daily_stats = BashOperator(
            task_id = "agg_daily_stats",
            bash_command = "cd /opt/airflow/dbt/transform_layer && dbt run"
        )

        get_heart_rate >> load_heart_rate >> get_and_load_runs >> agg_daily_stats