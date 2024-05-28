# Scrubbed Services

## Flink

KSQL requires less expertise and has a smaller learning curve than Flink. Based on my explorations into Flink
here i think it's an incredibly powerful tool, however I'm not sure the juice is worth the squeeze when we can much more
quickly take advantage of KSQL. An article on Confluent's site really helped articulate this for me, and would recommend
reading [Flink vs Kafka Streams/ksqlDB: Comparing Stream Processing Tools](https://developer.confluent.io/learn-more/podcasts/flink-vs-kafka-streams-ksqldb-comparing-stream-processing-tools/)
before looking to implement or utilize Flink, and make sure it's the right tool for the job, and not a solution looking
for a problem.

## Trino

It ended up being more effort to implement than i expected. I think it's a great tool, but for the purposes of this
project, it was overkill. I would recommend it for larger projects where you need to query multiple data sources, or
need to query data in a distributed manner. May come back to it in the future, but for now, it's on the shelf.