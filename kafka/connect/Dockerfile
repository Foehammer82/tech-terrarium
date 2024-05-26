FROM confluentinc/cp-kafka-connect:7.6.1

RUN confluent-hub install --no-prompt confluentinc/kafka-connect-jdbc:latest
RUN confluent-hub install --no-prompt mongodb/kafka-connect-mongodb:latest
RUN confluent-hub install --no-prompt confluentinc/kafka-connect-datagen:latest

# Copy in predefined connector configurations
COPY ./default_connector_configs /default_connector_configs
ENV DEFAULT_CONNECTOR_CONFIGS_DIR=/default_connector_configs

# Run the custom startup script
COPY ./startup.sh ./startup.sh
CMD ["sh", "./startup.sh"]
