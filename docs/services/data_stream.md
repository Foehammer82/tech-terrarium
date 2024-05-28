# Data Stream

## Kafka

Distributed streaming platform that is used for building real-time data pipelines and streaming applications. It is
used for publishing and subscribing to streams of records.

In this stack, Kafka is being used to stream data between services and as a source for Flink.

Alternatives: RabbitMQ, ActiveMQ, Pulsar

### KSQL - Query Kafka Streams with SQL

References:

- [KSQL — Getting Started (Part 1)](https://rasiksuhail.medium.com/ksql-getting-started-part-1-679df7eba28e)
- [KSQL — Getting Started (Part 2)](https://rasiksuhail.medium.com/ksql-getting-started-part-2-0949d0bb1c82)

## Scrubbed Services

### Flink

KSQL requires less expertise and has a smaller learning curve than Flink. Based on my explorations into Flink
here i think it's an incredibly powerful tool, however I'm not sure the juice is worth the squeeze when we can much more
quickly take advantage of KSQL. An article on Confluent's site really helped articulate this for me, and would recommend
reading [Flink vs Kafka Streams/ksqlDB: Comparing Stream Processing Tools](https://developer.confluent.io/learn-more/podcasts/flink-vs-kafka-streams-ksqldb-comparing-stream-processing-tools/)
before looking to implement or utilize Flink, and make sure it's the right tool for the job, and not a solution looking
for a problem.
