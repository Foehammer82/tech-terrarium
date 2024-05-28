# DockerHub Page: https://hub.docker.com/r/apache/airflow
#  Documentation: https://airflow.apache.org/docs/docker-stack/build.html
FROM apache/airflow:slim-2.9.1-python3.11

# Install Pre-requisites
USER root
RUN apt update && apt install -y postgresql gcc libpq-dev
USER airflow

# Install additional packages
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Initialize Airflow DB
RUN airflow db init
RUN airflow users  create --role Admin --username admin --email admin --firstname admin --lastname admin --password admin

# Configure Airflow
ENV AIRFLOW__DATABASE__LOAD_DEFAULT_CONNECTIONS='false'
ENV AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION='true'
ENV AIRFLOW__CORE__LOAD_EXAMPLES='false'

# Integrated with DataHub
ENV AIRFLOW_CONN_DATAHUB_REST_DEFAULT='{"conn_type": "datahub-rest", "host": "http://datahub-gms:8080"}'
ENV AIRFLOW__DATAHUB__ENABLED='true'

# set default command to run init scripts
COPY init.sh /init.sh
