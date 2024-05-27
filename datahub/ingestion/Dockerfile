FROM python:3.11-slim

# Install dependencies
RUN pip install acryl-datahub[kafka,kafka-connect,mongodb,postgres,metabase,dbt,mlflow,datahub-rest]

# Set ENV variables
COPY ingestion_configs /ingestion_configs
ENV INGESTION_CONFIGS_DIR = "/ingestion_configs"

# Copy application files
COPY do_ingestion.sh ./do_ingestion.sh

# TODO: get this moved into a crontab task that will run indefinitely on a schedule
# Run the ingestion script right away, and then every xx minutes
CMD ./do_ingestion.sh
# && */30 * * * * ./do_ingestion.sh
#    -   - - - -
#    |   | | | |
#    |   | | | ----- Day of the week (0 - 7) (Sunday=0 or 7)
#    |   | | ------- Month (1 - 12)
#    |   | --------- Day of the month (1 - 31)
#    |   ----------- Hour (0 - 23)
#      ------------- Minute (0 - 59)