FROM apache/airflow:2.5.1-python3.8

# Install system dependencies
USER root
RUN apt-get update && apt-get install -y gcc python3-dev

# Switch back to the airflow user
USER airflow

ADD requirements.txt .
ADD .env .
RUN pip install -r requirements.txt