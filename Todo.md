# Tracker

An ELT pipeline to fetch personal health and content consumption data from APIs, stage them in a central db (POSTGRES) and perform necessary transformations to extract stats/trends to display on a simple dashboard

## Extraction

### Health Data

The health data is extracted from fitbit and Strava


### Todo

Things to fix:
- Make fitbit module to a class
- Explore Fitbit Endpoints and pick any other ones to use
- Remove dependence on csvs as an interim, use Xcom instead or other ephemeral option
- Backup to S3 periodically
- Pydantic for API response 
- Runs fetch picks up a range not a specific date


Ideas for data processing
- Find resting heartrate
- Duration watch worn
- Time spent in each zone

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

#### Process FLow

- Check Internet Connection: The `InternetConnectionSensor` sensor checks if there is internet connectivity, it allows the next set of steps if there is network connectivity else it keeps retrying after 2 mins for a max period of an hour before stopping the process with a Network Connectivity error



Versions

V1:
- Dockerized postgres + airflow
- Single DAG which pulls heartrate data and sticks it into POSTGRES table

V2:
- Separate fitbit module that contains code to pull in heartrate data
    Talk about benefits of using try and except statements to control error prompting
- Another method to pull data for runs

V3:
- Another schema called heartrate_silver to integrate data from two tables using dbt
- Add SQL steps to perform the processing steps

Vx:
- Add sensor to check for internet connection
- Off load API data validation and the data type conversion to Pydantic