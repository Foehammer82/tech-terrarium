# Foehammer's Tech-Terrarium

Foehammer's Tech-Terrarium is a comprehensive ecosystem of services designed for testing, learning, and development
purposes. The project aims to simulate a tech stack in a small local environment, providing a hands-on experience with
various tools and technologies.

There are some coded applications within this environment, we chose to implement them in Python for simplicity and speed
to deployment, but the idea is that any Python app here could be re-written in another language.

> All services deployed in the Tech-Terrarium are open source and free to use. The project is intended for educational
> purposes, and designed to be run on inexpensive commodity hardware like Raspberry Pi's.

```mermaid
graph LR
    A[FastAPI] -->|Caches Data To| B[Redis]
    A -->|Interacts with| D[Kafka]
    F[GitHub Source Connector] -->|Feeds Data To| D
    D -->|Interacts with| E[PostgreSQL Sink Connector]
    E -->|Ingests data into| L[PostgreSQL]
    U -->|Offline Feature Store| L
    L -->|Admin Web Interface| M[pgAdmin]
    A -->|Interacts with| G
    D -->|Stateful Computations With| G[Flink]
    L -->|Data Analytics Source For| K[Metabase]
    I[MongoDB] -->|Admin Web Interface| J[Mongo Express]
    I -->|Data Analytics Source For| K
    O[Airflow] -->|Orchestrates| P[DBT]
    P -->|Operates on| L
    Q[DataHub / OpenMetadata] -->|Tracks metadata of| B
    Q -->|Tracks metadata of| I
    Q -->|Tracks metadata of| L
    Q -->|Tracks metadata of| K
    Q -->|Tracks metadata of| O
    Q -->|Tracks metadata of| T[MlFlow]
    Q -->|Tracks metadata of| E
    Q -->|Tracks metadata of| D
    Q -->|Tracks metadata of| P
    Q -->|Tracks metadata of| U
    T -->|Feature Store| U[Feast]
    U -->|Online Feature Store| B
```

## Usage

TODO: Add usage instructions (makefile and manual running and whatnot)

## Services

### PostgreSQL - Relational Database

Relational database that stores data in tables with rows and columns. It is used to store structured data and is
commonly used in enterprise applications.

Alternatives: MySQL, SQLite, Oracle

### MongoDB - NoSQL Database

NoSQL database that stores data in JSON-like documents with dynamic schemas. It is used to store unstructured data and

Alternatives: CouchDB, Cassandra, HBase

### Redis - In-Memory Data Store

In-memory data store that supports various data structures like strings, hashes, lists, sets, and sorted sets. It is
used for caching, session storage, and real-time analytics.

In this stack, Redis is being used for FastAPI caching and the online feature store registry for Feast.

Alternatives: Memcached, Hazelcast, Apache Ignite

### Kafka - Distributed Streaming Platform

Distributed streaming platform that is used for building real-time data pipelines and streaming applications. It is
used for publishing and subscribing to streams of records.

In this stack, Kafka is being used to stream data between services and as a source for Flink.

Alternatives: RabbitMQ, ActiveMQ, Pulsar

### FastAPI - Web Framework

Web framework for building APIs with Python. It is used for creating RESTful APIs with high performance and easy
development.

### gRPC - Remote Procedure Call Framework

Remote procedure call framework that is used for communication between services. It is used for defining services and
methods in a protocol buffer format.

### Flink - Stream Processing Framework

Stream processing framework that is used for processing unbounded and bounded data streams. It is used for stateful
computations on real-time data.

### Airflow - Workflow Scheduler

Workflow scheduler that is used for orchestrating complex data pipelines. It is used for scheduling
tasks/jobs/workflows and monitoring them.

Alternatives: Luigi, Prefect, Dagster

### Metabase - Business Intelligence Tool

Business intelligence tool that is used for visualizing and analyzing data. It is used for creating dashboards and
reports.

Alternatives: Tableau, Power BI, Looker

### MlFlow - Machine Learning Lifecycle Tool

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

Data transformation tool that is used for transforming data in the data warehouse. It is used for writing SQL queries
to transform data and create data models.

Alternatives: Apache Spark, Talend, Matillion

## TODO

- [x] set up a mkdocs site to document the terrarium
- [ ] add pre-commit checks to the project
- [ ] set up the FastAPI to utilize redis caching so that we can see data moving into redis and then utilize that data
  elsewhere
- [x] set up a project homepage using [Homepage](https://github.com/gethomepage/homepage) or something similar to make a
  single point of entry for all the services in the Terrarium.
- [ ] Kafka Connectors
    - [PostgreSQL Sink](https://docs.confluent.io/cloud/current/connectors/cc-postgresql-sink.html)
    - [GitHub Source](https://docs.confluent.io/cloud/current/connectors/cc-github-source.html)
        - would be neat to have this project be able to track change to itself from GitHub and any/all supporting
          projects (i.e. postgres,confluent,fastapi,etc. repos)
- [ ] Set up Flink
    - https://flink.apache.org/
    - https://docs.confluent.io/cloud/current/flink/overview.html
    - would be neat to see if it's possible or how much effort it would be to set up a GraphQL interface to Flink to
      enable querying of kafka data from a web client. but really just want to get a little more familiar with Flink as
      I've seen it referenced a few times now from large sources (i.e. Confluent)
- [ ] setup example python snippets in the kafka directory
    - basic dict/pydantic producer
    - avro producer (using pydantic)
    - basic consumer
    - avro consumer
    - async usage example
- [ ] set up a Makefile to make it easier to run the services and start the Terrarium, parts of the terrarium.
- [ ] build out the airflow instance with DAG's that perform scheduled operations on the rest of the terrarium
    - implement a DBT repo/project to be orchestrated by airflow
- [ ] setup metabase with some default dashboards for the terrarium
- [ ] dig deeper into MlFlow to expand knowledge and experience with building and releasing models.
    - might be worth setting up a feast repo/project for online/offline features stores for a model utilizing postgres
      and redis for practice.
- [ ] set up a Spark server and explore that more
    - follow the quick start guide to get a feel for it and operate on local files (testing parquet, csv, json, avro,
      etc.)
    - see about setting up apache iceberg locally and having Spark operate on it.
- [ ] implement DataHub to track metadata of the terrarium
    - would also not be a terrible idea to set up an instance of openmetadata as well.
- [ ] instead of deploying the docs locally with a container, have them deployed from Gitlab instead and then update the
  links in the homepage

## Long Term

- [ ] configure all exposed services to run through a Traefik load balancer
    - this would be a good exercise in setting up a reverse proxy and load balancer for the terrarium
- [ ] configure to run everything on kubernetes with helm. the goal is to see if the whole stack can be deployed on 3
  raspberry pi's using k3s.
    - write docs and instructions on setting up the hardware
    - write docs and instructions on setting up the k3s cluster
    - write docs and instructions for deploying the stack on the cluster

## Dropped Services

- Trino
    - Reason: it's been giving me nothing but challenges and didn't just work out of the box with kafka, which was a
      main goal for me. will take a look at using flink next for stream processing. Definatly a nice tool, but the
      given the overhead of setting it up, it's not worth it for this project, and would be a tough to consider
      pushing for in an enterprise environment without a clear need (don't need a solution looking for a problem).
