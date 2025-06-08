__all__ = ['get_heartrate', 'get_logged_runs']

import os
import pandas as pd
from datetime import datetime, timedelta
import requests
import dotenv
import pendulum
import logging
from src.logger import AirflowLogger
from src.models import schema

dotenv.load_dotenv()

src_dir = os.path.dirname(os.path.abspath(__file__))
repo_dir = os.path.dirname(src_dir)
output_dir = os.path.join(repo_dir,'output')

logging.basicConfig(level=logging.INFO)


# Setup Logger
logger = AirflowLogger('fitbit_pull_dag')


access_token=os.getenv('access_token')

headers = {
            'Authorization': f'Bearer {access_token},'
        }
        

def store_csv(df_heartrate_yesterday):
    """
    Stores the csv to the output folder
    """
    yesterday = datetime.now() - timedelta(days=1)
    yesterday = yesterday.strftime('%Y-%m-%d')

    df_heartrate_yesterday.to_csv(f'{output_dir}/heartrate_{yesterday}.csv',index=False)


def get_logged_runs(n_days: int):
    """
    Fetches the logged runs data for the last n days

    Args:
    -----
    n_days: Number of days to look back

    Return:
    -------
    df_runs: Dataframe with the run details
    """
    pt = pendulum.timezone('America/Los_Angeles')
    end_date = datetime.now(pt).strftime('%Y-%m-%d')
    start_date = (datetime.now(pt) - timedelta(days=n_days)).strftime('%Y-%m-%d')

    url = f"https://api.fitbit.com/1/user/-/activities/list.json?afterDate={start_date}&sort=desc&offset=0&limit=100"

    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        logging.error(f'API call failed with status: {response.status_code}')
        return None

    response_json = response.json()
    activities = response_json.get('activities', [])

    # Filter for run activities
    run_activities = [activity for activity in activities if activity['activityName'] == 'Run']

    df_runs = pd.DataFrame(run_activities)

    if not df_runs.empty:

        # Select and rename relevant columns
        columns_to_keep = ['startTime', 'duration', 'distance', 'pace', 'speed', 'calories']
        df_runs = df_runs[columns_to_keep]
        df_runs = df_runs.rename({
            'startTime': 'run_start_time',
            'duration': 'duration_ms',
            'distance': 'distance_km',
            'pace': 'pace_min_km',
            'speed': 'speed_km_h',
            'calories': 'calories_burned'
        }, axis=1)
        
        df_runs['run_start_time'] = pd.to_datetime(df_runs['run_start_time'])

        # Calculate date from run start time
        df_runs['date'] = df_runs['run_start_time'].dt.date

        # Compute start time
        df_runs['start_time'] = df_runs['run_start_time'].dt.strftime('%H:%M:%S')

        # Convert duration from milliseconds to minutes
        df_runs['duration_minutes'] = df_runs['duration_ms'] / 60000

        # Calculate the end time
        df_runs['time_delta_start'] = pd.to_timedelta(df_runs['start_time'])
        df_runs['end_time'] = (df_runs['time_delta_start'] + pd.to_timedelta(df_runs['duration_minutes'], unit='m'))
        
        df_runs['end_time'] = (pd.to_datetime('2004-01-30') + df_runs['end_time']).dt.strftime('%H:%M:%S')

        df_runs['duration_minutes'] = (df_runs['duration_minutes']).round(2)
        # df_runs['end_time'] = df_runs['end_time'].astype(str)           

        # Convert distance from kilometers to miles
        df_runs['distance_miles'] = (df_runs['distance_km'] * 0.621371).round(2)

        # Convert pace from min/km to min/mile
        df_runs['pace_min_mile'] = (df_runs['pace_min_km'] / 0.621371).round(2)

        # Convert speed from km/h to mph
        df_runs['speed_mph'] = (df_runs['speed_km_h'] * 0.621371).round(2)

        # Reorder columns
        df_runs = df_runs[['date', 'start_time', 'end_time', 'duration_minutes', 'distance_miles', 'pace_min_mile', 'speed_mph', 'calories_burned']]

        df_runs['data_insert_timestamp'] = datetime.now()
        
        logging.info(f"Successfully extracted run data: {df_runs.head()}")

        logging.info(f"Successfully extracted run data: {df_runs.head()}")

    else:
        logging.info("No data retrieved")

    return df_runs

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


if __name__=='__main__':
    df_heartrate = get_heartrate()

    store_csv(df_heartrate)