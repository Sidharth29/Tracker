# Tracker

An ELT pipeline to fetch personal health and content consumption data from APIs, stage them in a central db (POSTGRES) and perform necessary transformations to extract stats/trends to display on a simple dashboard

# Extraction

### Health Data

The health data is extracted from fitbit and Strava 



# Enter docker container using bash
docker exec -it 36244bbcc32e bash


# Step into POSTGRES db
psql -h localhost -p 5430 -U admin -d health_monitor_db

