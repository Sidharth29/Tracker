## Useful commands

# Building Up services
docker compose build --no-cache

# Spinning them up
docker compose up -d

# Checking logs
docker compose logs airflow-init

# Clearing unused caches
docker system prune -a # Clears all images (Careful)


### Enter docker container using bash
docker exec -it 36244bbcc32e bash


## POSTGRES

### Step into POSTGRES db
psql -h localhost -p 5430 -U admin -d health_monitor_db


- Check for schema

```
\dn
```

- Check for table within schema

```
\dt heartrate.*
```




### Push to git

git push https://Sidharth29:{PAT}@github.com/Sidharth29/Tracker.git

## Useful Links

Spinning up a dockerized version of airflow


# Notes
- **Update the Dockerfile to remove the platform part if you're not using an M1 MAC** 
- Framing the connect string to connect to the db
    - Hostname: This is the service name defined in the docker-compose file for the database (ex: db) not localhost (what we use locally)
    - Port: This the mapped port number on the docker end (ex: 5432) not one used locally (ex: 5430)  

### TODO

- Create the table structure for the POSTGRES tables within each schema (gold and silver)
- Add the schema and table creation to the docker build