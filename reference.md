# Enter docker container using bash
docker exec -it 36244bbcc32e bash


# Step into POSTGRES db
psql -h localhost -p 5430 -U admin -d health_monitor_db

# Useful Links

Spinning up a dockerized version of airflow
