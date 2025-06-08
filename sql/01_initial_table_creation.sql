-- CREATE REQUIRED SCHEMAS

CREATE SCHEMA heartrate;

CREATE SCHEMA runs;

CREATE SCHEMA heartrate_silver;


-- CREATE the all_runs table to store the logged runs data

CREATE TABLE heartrate.heartrate_data (
    date VARCHAR,
    time VARCHAR,
    heartrate INTEGER,
    data_insert_timestamp TIMESTAMP
);


-- CREATE the all_runs table to store the logged runs data

CREATE TABLE runs.all_runs (
    date DATE,
    start_time TIME,
    end_time TIME,
    duration_minutes DECIMAL(10,2),
    distance_miles DECIMAL(10,2),
    pace_min_mile DECIMAL(10,2),
    speed_mph DECIMAL(10,2),
    calories_burned INTEGER,
    data_insert_timestamp TIMESTAMP
);