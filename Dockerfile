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
    libpq5=13.14-0+deb11u1


# Switch back to the airflow user
USER airflow

ADD requirements.txt .
ADD .env .
RUN pip install -r requirements.txt