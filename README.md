# Tracker

An ELT pipeline to fetch personal health and content consumption data from APIs, stage them in a central db (POSTGRES) and perform necessary transformations to extract stats/trends to display on a simple dashboard

## Extraction

### Health Data

The health data is extracted from fitbit and Strava


### Todo

-Create the main schemas (heartrate,runs and heartrate_silver) and tables (heartrate_data and all_runs) during docker build
-Option to backup data on S3