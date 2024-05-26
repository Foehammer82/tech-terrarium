FROM confluentinc/cp-kafka-connect:7.6.1

RUN confluent-hub install --no-prompt confluentinc/kafka-connect-jdbc:latest
RUN confluent-hub install --no-prompt mongodb/kafka-connect-mongodb:latest
RUN confluent-hub install --no-prompt confluentinc/kafka-connect-datagen:latest

COPY ./connect-startup.sh ./connect-startup.sh
#CMD ["sh", "./connect-startup.sh"]
