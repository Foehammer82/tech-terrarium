FROM confluentinc/cp-kafka-connect:7.6.1

RUN confluent-hub install --no-prompt confluentinc/kafka-connect-jdbc:latest
RUN confluent-hub install --no-prompt mongodb/kafka-connect-mongodb:latest
RUN confluent-hub install --no-prompt confluentinc/kafka-connect-datagen:latest

# DEFAULT RUN SCRIPT: https://github.com/confluentinc/kafka-images/blob/master/server/include/etc/confluent/docker/run
COPY ./startup.sh ./startup.sh
CMD ["sh", "./startup.sh"]
