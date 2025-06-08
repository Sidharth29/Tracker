from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.bash import BashOperator
from airflow.sensors.base import BaseSensorOperator
from airflow.utils.decorators import apply_defaults
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.load_to_db import health_db
from src.fitbit import get_logged_runs
from src.utils import generate_date_list
from src.models import schema
from src.logger import AirflowLogger

from random import randint
from datetime import datetime, timedelta
import pandas as pd
import os
import requests
from airflow.utils.log.logging_mixin import LoggingMixin
import logging
import pendulum
import dotenv
import time

dotenv.load_dotenv()


# Setup Logger
logger = AirflowLogger('fitbit_pull_dag')


src_dir = os.path.dirname(os.path.abspath(__file__))
repo_dir = os.path.dirname(src_dir)
output_dir = os.path.join(repo_dir,'output')

access_token="eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIyM1JYRFIiLCJzdWIiOiI5V1QzQkgiLCJpc3MiOiJGaXRiaXQiLCJ0eXAiOiJhY2Nlc3NfdG9rZW4iLCJzY29wZXMiOiJyc29jIHJlY2cgcnNldCByb3h5IHJudXQgcnBybyByc2xlIHJjZiByYWN0IHJsb2MgcnJlcyByd2VpIHJociBydGVtIiwiZXhwIjoxNzQ2ODUyNjI0LCJpYXQiOjE3MTUzMTY5OTR9.xcJoIi_O8rYh-sVXUbc0bBOk1JYCuLzYhzB3hJ9Tx1c"

headers = {
            'Authorization': f'Bearer {access_token}'
        }



class InternetConnectionSensor(BaseSensorOperator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def poke(self, context):
        """Check if we can reach the Fitbit API endpoint"""
        logger.info("Checking internet connectivity...")
        try:
            requests.get("https://api.fitbit.com", timeout=5)
            logger.info("Internet connection established")
            return True
        except requests.RequestException:
            return False


def get_heartrate(dt: str = None):
    """
    Fetches the heart rate date from yesterday
    """
        
    try:
        # Get latest date to fetch data - yesterday
        pt = pendulum.timezone('America/Los_Angeles')

        # If no date provided, use yesterday
        if dt is None:
            dt = (datetime.now(pt) - timedelta(days=1)).strftime('%Y-%m-%d')

        url = f"https://api.fitbit.com/1/user/-/activities/heart/date/{dt}/1d/1min/time/00:00/23:59.json"
            # Add timeout to the request
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        response_json = response.json()

        # Extract and validate response by loading it to a pydantic model
        heartrate_response = schema.HeartrateResponse(**response_json)
        heartrate_response_intraday = schema.HeartrateResponseList(**heartrate_response.activities)
        df_heartrate = heartrate_response_intraday.to_dataframe()
        
        # Add date and data insert timestamp
        df_heartrate['date'] = dt
        df_heartrate['data_insert_timestamp'] = datetime.now(pt)
        logger.info(f"Successfully extracted data for {dt}: {df_heartrate.head()}")
        
        return df_heartrate
   
    except requests.RequestException as e:
        logger.error(f"Network error for date {dt}: {str(e)}")
        raise

    return None

def _get_heartrate():
    """
    Fetches the heart rate data till yesterday with robust error handling and internet checks
    """
    
    # Get latest date to fetch data - yesterday
    pt = pendulum.timezone('America/Los_Angeles')
    yesterday = datetime.now(pt) - timedelta(days=1)
    
    try:
        # Get latest date loaded into db
        max_date = health_db.get_latest_date(
            table_name='heartrate_daily', 
            schema='heartrate_silver', 
            date_field="date"
        )
    except Exception as e:
        logger.warning(f"Failed to get latest date from DB: {str(e)}")
        max_date = yesterday - timedelta(days=1)
    
    # Date range to extract data
    date_range = generate_date_list(start_date=max_date, end_date=yesterday.date())
    
    if not date_range:
        logger.info("No new dates to process")
        return

    logger.info(f"Processing dates: {date_range}")

    for dt in date_range:
        dt_formatted = dt.strftime('%Y-%m-%d')
        # url = f"https://api.fitbit.com/1/user/-/activities/heart/date/{dt_formatted}/1d/1min/time/00:00/23:59.json"
        
        try:
            df_heartrate = get_heartrate(dt=dt_formatted)
            
            # Load data to a directory
            os.makedirs(output_dir, exist_ok=True)
            output_path = f'{output_dir}/heartrate_{dt}.csv'
            logger.info(f'Storing file {output_path}')
            df_heartrate.to_csv(output_path, index=False, mode='w')
            
        except Exception as e:
            logger.error(f"Error processing data for date {dt}: {str(e)}")
            continue
    
    # If we get here without raising an exception, break the retry loop
    logger.info("Successfully completed heart rate data extraction")
            
            
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
        'retries': 3,
        'retry_delay': timedelta(minutes=10),  # Longer delay between retries
        'retry_exponential_backoff': True,  # Exponential backoff for retries
        'max_retry_delay': timedelta(hours=2)  # Maximum delay between retries
         },
         description='A DAG to pull Heartrate from Fitbit API and store as CSV',
         start_date=datetime(2024,5,11), \
         schedule_interval='0 18 * * *',
         catchup=False) as dag:
        
        check_connection = InternetConnectionSensor(
                                                    task_id='check_internet',
                                                    poke_interval=120,  # Check every 2 minutes
                                                    timeout=3600,  # Total timeout of 1 hr
                                                    mode='poke'
                                                )
            

        get_heart_rate = PythonOperator(
                                            task_id = "get_heart_rate",
                                            python_callable = _get_heartrate,
                                            retries=3,
                                            retry_delay=timedelta(minutes=10),
                                            execution_timeout=timedelta(hours=1)
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

        check_connection >> get_heart_rate >> load_heart_rate >> get_and_load_runs >> agg_daily_stats