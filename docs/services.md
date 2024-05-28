# Services

## PostgreSQL - Relational Database

Relational database that stores data in tables with rows and columns. It is used to store structured data and is
commonly used in enterprise applications.

Alternatives: MySQL, SQLite, Oracle

## MongoDB - NoSQL Database

NoSQL database that stores data in JSON-like documents with dynamic schemas. It is used to store unstructured data and

Alternatives: CouchDB, Cassandra, HBase

## Redis - In-Memory Data Store

In-memory data store that supports various data structures like strings, hashes, lists, sets, and sorted sets. It is
used for caching, session storage, and real-time analytics.

In this stack, Redis is being used for FastAPI caching and the online feature store registry for Feast.

Alternatives: Memcached, Hazelcast, Apache Ignite

## Kafka - Distributed Streaming Platform

Distributed streaming platform that is used for building real-time data pipelines and streaming applications. It is
used for publishing and subscribing to streams of records.

In this stack, Kafka is being used to stream data between services and as a source for Flink.

Alternatives: RabbitMQ, ActiveMQ, Pulsar

### KSQL - Query Kafka Streams with SQL

#### References

- [KSQL — Getting Started (Part 1)](https://rasiksuhail.medium.com/ksql-getting-started-part-1-679df7eba28e)
- [KSQL — Getting Started (Part 2)](https://rasiksuhail.medium.com/ksql-getting-started-part-2-0949d0bb1c82)

## FastAPI - Web Framework

Web framework for building APIs with Python. It is used for creating RESTful APIs with high performance and easy
development.

## Airflow - Workflow Scheduler

Workflow scheduler that is used for orchestrating complex data pipelines. It is used for scheduling
tasks/jobs/workflows and monitoring them.

Alternatives: Luigi, Prefect, Dagster

## Metabase - Business Intelligence Tool

Business intelligence tool that is used for visualizing and analyzing data. It is used for creating dashboards and
reports.

Alternatives: Tableau, Power BI, Looker

## MlFlow - Machine Learning Lifecycle Tool

Machine learning lifecycle tool that is used for managing the end-to-end machine learning process. It is used for
tracking experiments, packaging code, and deploying models.

### Feast - Feature Store

Feature store that is used for managing and serving machine learning features. It is used for storing and serving
features for training and serving machine learning models.

### DataHub - Metadata Management Tool

Metadata management tool that is used for tracking metadata of data assets. It is used for discovering, understanding,
and governing data assets.

Alternatives: Apache Atlas, Amundsen, Data Catalog, OpenMetadata, Alation

### DBT - Data Transformation Tool

!!! note

    I can not recommend DBT enough. It's a fantastic tool for transforming data and creating data models. My only 
    wish is that I had used it sooner on previous projects that it was LITERALLY designed to solve.

Data transformation tool that is used for transforming data in the data warehouse. It is used for writing SQL queries
to transform data and create data models.

Alternatives: Apache Spark, Talend, Matillion

#### References

- [Is DBT the right tool for my data transformations?](https://www.getdbt.com/blog/is-dbt-the-right-tool-for-my-data-transformations)
- [The Spiritual Alignment of dbt + Airflow](https://docs.getdbt.com/blog/dbt-airflow-spiritual-alignment#dbt-core--airflow)
- [Orchestrating dbt with Airflow: A Step by Step Guide to Automating Data Pipelines — Part I](https://rasiksuhail.medium.com/orchestrating-dbt-with-airflow-a-step-by-step-guide-to-automating-data-pipelines-part-i-7a6db8ebc974)
- [Orchestrating dbt with Airflow: A Step by Step Guide to Automating Data Pipelines — Part II](https://rasiksuhail.medium.com/orchestrating-dbt-with-airflow-a-step-by-step-guide-to-automating-data-pipelines-part-ii-3f53616c3832)

## Scrubbed Services

Below is are services that I had looked at including in the Tech-Terrarium, but have since decided to remove for one
reason or another.

### Trino

Reason:

- it's been giving me nothing but challenges and didn't just work out of the box with kafka, which was a
  main goal for me. will take a look at using flink next for stream processing. Definatly a nice tool, but the
  given the overhead of setting it up, it's not worth it for this project, and would be a tough to consider
  pushing for in an enterprise environment without a clear need (don't need a solution looking for a problem).

### Flink - Stream Processing Framework

Reason: KSQL requires less expertise and has a smaller learning curve than Flink. Based on my explorations into Flink
here i think it's an incredibly powerful tool, however I'm not sure the juice is worth the squeeze when we can much more
quickly take advantage of KSQL. An article on Confluent's site really helped articulate this for me, and would recommend
reading [Flink vs Kafka Streams/ksqlDB: Comparing Stream Processing Tools](https://developer.confluent.io/learn-more/podcasts/flink-vs-kafka-streams-ksqldb-comparing-stream-processing-tools/)
before looking to implement or utilize Flink, and make sure it's the right tool for the job, and not a solution looking
for a problem.
