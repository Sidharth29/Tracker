#!/bin/bash
set -e

# Airflow needs the $AIRFLOW_HOME/airflow.cfg file to exist before we can run any commands
if [ ! -f "$AIRFLOW_HOME/airflow.cfg" ]; then
    airflow version
fi

case "$1" in
  webserver|worker|scheduler|flower|triggerer|celery|version)
    exec airflow "$@"
    ;;
  *)
    exec "$@"
    ;;
esac