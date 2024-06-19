import os
import pandas as pd
import datetime
import requests

src_dir = os.path.dirname(os.path.abspath(__file__))
repo_dir = os.path.dirname(src_dir)
output_dir = os.path.join(repo_dir,'output')


access_token="eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIyM1JYRFIiLCJzdWIiOiI5V1QzQkgiLCJpc3MiOiJGaXRiaXQiLCJ0eXAiOiJhY2Nlc3NfdG9rZW4iLCJzY29wZXMiOiJyc29jIHJlY2cgcnNldCByb3h5IHJudXQgcnBybyByc2xlIHJjZiByYWN0IHJsb2MgcnJlcyByd2VpIHJociBydGVtIiwiZXhwIjoxNzQ2ODUyNjI0LCJpYXQiOjE3MTUzMTY5OTR9.xcJoIi_O8rYh-sVXUbc0bBOk1JYCuLzYhzB3hJ9Tx1c"

headers = {
            'Authorization': f'Bearer {access_token},'
        }



def get_yesterday_heartrate():
    """
    Fetches the heart rate date from yesterday
    """

    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    yesterday = yesterday.strftime('%Y-%m-%d')

    url = f"https://api.fitbit.com/1/user/-/activities/heart/date/{yesterday}/1d/1min/time/00:00/23:59.json"

    response = requests.get(url, headers=headers)

    response_json = response.json()

    heartrate_data = response_json['activities-heart-intraday']['dataset']
        
    df_heartrate = pd.DataFrame(heartrate_data)

    df_heartrate['date'] = yesterday

    df_heartrate = df_heartrate.rename({'value':'heartrate'}, axis=1)

    return df_heartrate[['date','time','heartrate']]




def store_csv(df_heartrate_yesterday):
    """
    Stores the csv to the output folder
    """
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    yesterday = yesterday.strftime('%Y-%m-%d')

    df_heartrate_yesterday.to_csv(f'{output_dir}/heartrate_{yesterday}.csv',index=False)


if __name__=='__main__':
    df_heartrate = get_yesterday_heartrate()

    store_csv(df_heartrate)