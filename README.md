# Tracker

An ELT pipeline to fetch personal health and content consumption data from APIs, stage them in a central db (POSTGRES) and perform necessary transformations to extract stats/trends to display on a simple dashboard

## Extraction

### Health Data

The health data is extracted from fitbit and Strava


### Todo

Things to fix:
- Check if the DAG runs as soon as Docker turns on
- Actual run time and date for runs (not the UTC time)
- Runs fetch picks up a range not a specific date

#### Visualize Pipeline

Visualize the daily pipeline, the process flow and the end result

#### Auto Initialize Database

- In the docker build process, include a step to
    - Create the schema and tables
    - Populate them with data from S3
- CHeck if it's the very first run (if the database tables exist)

-Create the main schemas (heartrate,runs and heartrate_silver) and tables (heartrate_data and all_runs) during docker build

#### Archival DAG
- Option to backup data on S3 
- S3: Lifecycle policy to move data older than X months to Cheapest form of Glacier - Deep Archive

