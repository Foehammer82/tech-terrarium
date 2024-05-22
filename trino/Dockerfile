FROM trinodb/trino:448

# https://trino.io/docs/current/connector/kafka.html#requirements
ADD https://packages.confluent.io/maven/io/confluent/kafka-protobuf-provider/7.3.1/kafka-protobuf-provider-7.3.1.jar /lib/trino/plugin/kafka/
ADD https://packages.confluent.io/maven/io/confluent/kafka-protobuf-types/7.3.1/kafka-protobuf-types-7.3.1.jar /lib/trino/plugin/kafka/
