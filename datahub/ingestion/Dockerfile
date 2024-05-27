FROM python:3.11-slim

# Install dependencies
RUN pip install acryl-datahub[kafka,kafka-connect,mongodb,postgres,metabase,dbt,mlflow,datahub-rest]

# Install OpenJDK 11
RUN apt-get update \
 && apt-get upgrade -y \
 && apt-get install -y cron default-jre #software-properties-common openjdk-11-jdk
RUN java -version

# Set ENV variables
COPY ingestion_configs /ingestion_configs
ENV INGESTION_CONFIGS_DIR = "/ingestion_configs"

# Copy application files
COPY do_ingestion.sh ./do_ingestion.sh
COPY crontab /etc/cron.d/dh-ingestion-cron

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/dh-ingestion-cron

# Apply cron job
RUN crontab /etc/cron.d/dh-ingestion-cron

# Run the command on container startup
CMD ./do_ingestion.sh && cron -f
