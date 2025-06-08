import pandas as pd
import numpy as np
import os
from sqlalchemy import create_engine, text
import dotenv
import logging
import shutil
from datetime import datetime, timedelta
from src.logger import AirflowLogger
import pendulum

dotenv.load_dotenv()



#TODO: Add a logging handler class

logger = AirflowLogger('fitbit_pull_dag.data_load')


src_dir = os.path.dirname(os.path.abspath(__file__))
repo_dir = os.path.dirname(src_dir)
output_dir = os.path.join(repo_dir,'output')
postgres_logs = os.path.join(repo_dir,'logs','postgres_logs')


# Set up logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler(f'{postgres_logs}/postgres.log'),
                        logging.StreamHandler()
                    ])

# Database credentials
db_user = os.getenv("db_user")
db_password = os.getenv("db_password")
db_host = os.getenv("db_host")
db_port = os.getenv("db_port")
db_name = os.getenv("db_name")

#If db does not exist create db if it exists insert into db

class health_db:
    db_user = os.getenv("db_user")
    db_password = os.getenv("db_password")
    db_host = os.getenv("db_host")
    db_port = os.getenv("db_port")
    db_name = os.getenv("db_name")
   

    @classmethod
    def load_files_to_db(cls, keyword:str, table_name: str, schema: str):
        """
        Load contents of a directory (csv/parquet) to a database

        Args:
        -----
        keyword: The keyword to identify the filenames to load to the database

        Return:
        -------
        None
        """

        # Create a database engine
        engine = create_engine(f'postgresql+psycopg2://{cls.db_user}:{cls.db_password}@{cls.db_host}:{cls.db_port}/{cls.db_name}?options=-csearch_path={schema}')
        
        logger.info(f'Accessing database: {db_name}')
        logger.info(f"Loading data to table {table_name}")
        
        move_path = os.path.join(output_dir,'loaded_files',keyword)
        try:
            contents = os.listdir(output_dir)
            for file in contents:
                if (file.startswith(keyword) and file.endswith('.csv')):
                    filepath = os.path.join(output_dir, file)
                    df = pd.read_csv(filepath)
                    if "data_insert_timestamp" not in df.columns:
                        pt = pendulum.timezone('America/Los_Angeles')
                        df["data_insert_timestamp"] = datetime.now(pt)
                    logger.info(f'Filename: {file}, content: {df.head(2)}')
                    logger.info(f'Inserting {df.shape[0]} rows into table {schema}.{table_name}')
                    df.to_sql(table_name, engine, if_exists='append', index=False, schema=schema)
                    logger.info(f'Successfully inserted data from {filepath}')       
                    destination_path = os.path.join(move_path, file)
                    logger.info(f'Moving file to {move_path}')
                    if os.path.exists(destination_path):
                        os.remove(destination_path)
                    os.makedirs(os.path.dirname(move_path), exist_ok=True)
                    shutil.move(filepath, move_path)
        # except FileNotFoundError:
        #     logging.error(f"The directory {output_dir} does not exist.")
        except PermissionError:
            logger.error(f"Permission denied to access the directory {output_dir}.")


        logger.info(f"Db User: {db_user}")

    @classmethod
    def load_df_to_db(cls, df: pd.DataFrame, table_name: str, schema: str):
        """
        Loads contents of the provided dataframe to the POSTGRES table

        Args:
        -----
        df: The dataframe containing the data to be loaded
        table_name: the target table to update
        schema: The schema of the target table

        Return:
        ------- 
        None
        """

        # Create a database engine
        engine = create_engine(f'postgresql+psycopg2://{cls.db_user}:{cls.db_password}@{cls.db_host}:{cls.db_port}/{cls.db_name}?options=-csearch_path={schema}')

        # Upload data to table
        logger.info(f'Inserting {df.shape[0]} rows into table {schema}.{table_name}')
        df.to_sql(table_name, engine, if_exists='append', index=False, schema=schema)
        logger.info('Successfully inserted data to table')

    @classmethod
    def get_latest_date(cls, table_name: str, schema: str, date_field: str):
        """
        Load latest date from the table

        Args:
        -----
        table_name: The tablename within the database
        schema: The schema name
        date_field: the date field name to be used

        Return:
        -------
        None
        """

        # Create a database engine
        engine = create_engine(f'postgresql+psycopg2://{cls.db_user}:{cls.db_password}@{cls.db_host}:{cls.db_port}/{cls.db_name}?options=-csearch_path={schema}')

        query = f"SELECT max({date_field}) as max_date FROM {table_name}"

        with engine.connect() as connection:
            result = connection.execute(text(query))
            max_date = result.scalar()

        return max_date

    @classmethod
    def load_db_to_df(cls, table_name: str, schema: str) -> pd.DataFrame:
        """
        Load the contents of a database table to a pandas DataFrame
        
        Args:
        table_name (str): Name of the table to query
        schema (str): Schema name where the table is located
        
        Returns:
        pd.DataFrame: DataFrame containing the queried data
        """
        # Set up engine to communicate with the database
        engine = create_engine(f'postgresql+psycopg2://{cls.db_user}:{cls.db_password}@{cls.db_host}:{cls.db_port}/{cls.db_name}?options=-csearch_path={schema}')

        # Query to fetch the data from the database
        query = f'SELECT * FROM {schema}.{table_name}'

        try:
            # Fetch the data from the database and load into a DataFrame
            df = pd.read_sql_query(sql=text(query), con=engine)
            
            # # Convert date and time columns to appropriate dtypes
            # df['date'] = pd.to_datetime(df['date'])
            # df['start_time'] = pd.to_datetime(df['start_time'], format='%H:%M:%S').dt.time
            # df['end_time'] = pd.to_datetime(df['end_time'], format='%H:%M:%S').dt.time
            # df['data_insert_timestamp'] = pd.to_datetime(df['data_insert_timestamp'])
            
            # # Convert numeric columns to appropriate dtypes
            # numeric_columns = ['duration_minutes', 'distance_miles', 'pace_min_mile', 'speed_mph', 'calories_burned']
            # df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')
            
            return df
        
        except Exception as e:
            print(f"An error occurred: {e}")
            return pd.DataFrame()  # Return an empty DataFrame if there's an error
        
        finally:
            engine.dispose()  # Close the database connection


if __name__=='__main__':
    max_date = health_db.get_latest_date(table_name='heartrate_daily', schema='heartrate_silver', date_field="date")