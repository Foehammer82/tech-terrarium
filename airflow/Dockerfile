# DockerHub Page: https://hub.docker.com/r/apache/airflow
#  Documentation: https://airflow.apache.org/docs/docker-stack/build.html
FROM apache/airflow:slim-2.9.1-python3.11

# Install additional packages
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt