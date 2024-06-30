import pandas as pd
import numpy as np
import os
from sqlalchemy import create_engine
import dotenv
import logging
import shutil

dotenv.load_dotenv()



#TODO: Add a logging handler class


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
    def load_to_db(cls, keyword:str, table_name: str, schema: str):
        """
        Load contents of a directory (csv/parquet) to a database

        Args:
        -----
        keyword: The keyword to identify the filenames to load to the database
        """

        # Create a database engine
        engine = create_engine(f'postgresql+psycopg2://{cls.db_user}:{cls.db_password}@{cls.db_host}:{cls.db_port}/{cls.db_name}?options=-csearch_path={schema}')

        logging.debug(f'Accessing database: {db_name}')
        move_path = os.path.join(output_dir,'loaded_files',keyword)
        try:
            contents = os.listdir(output_dir)
            for file in contents:
                if (file.startswith(keyword) and file.endswith('.csv')):
                    filepath = os.path.join(output_dir, file)
                    df = pd.read_csv(filepath)
                    if "data_insert_timestamp" not in df.columns:
                        df["data_insert_timestamp"] = np.nan
                    logging.debug(f'Filename: {file}, content: {df.head(2)}')
                    logging.debug(f'Inserting {df.shape[0]} rows into table {schema}.{table_name}')
                    df.to_sql(table_name, engine, if_exists='append', index=False, schema=schema)
                    logging.debug(f'Successfully inserted data from {filepath}')
                    logging.debug(f'Moving file to {move_path}')
                    destination_path = os.path.join(move_path, file)
                    if os.path.exists(destination_path):
                        os.remove(destination_path)
                    shutil.move(filepath, move_path)
        # except FileNotFoundError:
        #     logging.error(f"The directory {output_dir} does not exist.")
        except PermissionError:
            logging.error(f"Permission denied to access the directory {output_dir}.")


        print(f"Db User: {db_user}")


if __name__=='__main__':
    health_db.load_to_db(keyword="heartrate", table_name='heartrate_data', schema='heartrate')
