# Enter docker container using bash
docker exec -it 36244bbcc32e bash


# Step into POSTGRES db
psql -h localhost -p 5430 -U admin -d health_monitor_db

# Push to git

git push https://Sidharth29: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@github.com/Sidharth29/Tracker.git