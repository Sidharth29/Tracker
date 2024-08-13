# Change the platform part if you're not using an M1 MAC
FROM --platform=linux/amd64 apache/airflow:2.5.1-python3.8 

# Install system dependencies
USER root
RUN apt-get update && apt-get install -y gcc python3-dev

# Use HTTP instead of HTTPS for the PostgreSQL repository to avoid certificate issues
RUN sed -i 's/https:\/\/apt.postgresql.org\/pub\/repos\/apt/http:\/\/apt.postgresql.org\/pub\/repos\/apt/g' /etc/apt/sources.list.d/pgdg.list

# Update package lists and install required packages with allow-downgrades
RUN apt-get update && apt-get install -y --no-install-recommends --allow-downgrades \
    gcc \
    python3-dev \
    libpq-dev=13.14-0+deb11u1 \
    git \
    libpq5=13.14-0+deb11u1


# Dbt setup
# Copy the entire dbt directory
COPY dbt /opt/airflow/dbt

# Set permissions for the airflow user
RUN chown -R airflow /opt/airflow/dbt

# Switch to airflow user
USER airflow

# Install dbt and dbt-postgres
RUN pip install dbt-core dbt-postgres


ADD requirements.txt .
ADD .env /opt/airflow/.env
RUN pip install -r requirements.txt


WORKDIR /opt/airflow/dbt/transform_layer

# Create necessary dbt directories if they don't exist
RUN mkdir -p models seeds snapshots tests macros analysis