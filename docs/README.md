<p align="center">
  <a href="./"><img src="./assets/terrarium.png" alt="Tech-Terrarium" width="200"></a>
</p>

# Tech-Terrarium

**Documentation**:
<a href="https://foehammer82.github.io/tech-terrarium/" target="_blank">https://foehammer82.github.io/tech-terrarium/</a>

**Source Code**:
<a href="https://github.com/Foehammer82/tech-terrarium" target="_blank">https://github.com/Foehammer82/tech-terrarium</a>

The Tech-Terrarium project is a compact hands-on tech stack simulation for learning and development. It comprises
a full stack of interconnected services that are commonly used in Data Engineering and Software Engineering projects.
Each service is set up to be deployed on docker using docker-compose. You will find each directory in this repo
containing a docker-compose.yaml file that will start the given service and its dependencies.

The Terrarium is designed such that each service can be run independently, though they also work in concert with
each-other. For example, you can start the kafka service which will start a broker, schema registry, ksqldb server,
an admin ui, and a few connectors. Two are configured to connect to the Terrarium's PostgreSQL and MongoDB services,
while a third is designed to ingest dummy data from a data generator. So you can start just Kafka and see how it works
and even develop against it. and you can start up the Postgres instance and see the kafka connector start sending data
to Postgres. The diagram below illustrates the services in the Terrarium and how they interact with each other.

## Motivation

I have often found myself digging through past projects to look up how different implementations were accomplished or
to reference a past approach. I have also commonly found myself re-researching the same things over and over again
throughout both personal and professional projects. Enter the `Tech-Terrarium`. This project is mostly for my own
benefit to be able to quickly spin up, look at, and play with different approaches to Data Engineering and Software
Engineering problems. And, if this helps someone else along the way, then that's a bonus!

That said, if you do find yourself here and have questions, comments, feedback, or suggestions, please feel free to
reach out or start create an `Issue` or `Pull Request`. And, this should go without saying, but please be
respectful and considerate when making comments or suggestions.

## Project Architecture

```mermaid
graph LR
    U -->|Sends Audit Data To| B
    G[Feast] -->|Offline Feature Store| E
    A[FastAPI App] -->|Sends Audit Data To| B[Kafka]
    G -->|Online Feature Store| V[Redis]
    Q -->|Tracks metadata of| E
    Q -->|Tracks metadata of| B
    Q -->|Tracks metadata of| D
    B -->|Streams Data To| D[PostgreSQL Sink Connector]
    A -->|Interacts With| E
    D -->|Streams Data Into| E[PostgreSQL]
    Q -->|Tracks metadata of| G
    U -->|Gets Features From| G
    A -->|Interacts With| U
    H -->|BI Data Analytics Against| I
    T[MlFlow] -->|Manages Lifecycle for| U(Model)
    F[MongoDB Sink Connector] -->|Streams Data Into| I
    B -->|Streams Data To| F
    O -->|Performs Data Operations On| I
    Q[DataHub] -->|Tracks metadata of| I[MongoDB]
    Q -->|Tracks metadata of| H
    Q -->|Tracks metadata of| O[Airflow]
    O -->|Publishes To| B
    O -->|Performs Data Operations On| E
    H[Metabase] -->|BI Data Analytics Against| E
    Q -->|Tracks metadata of| T
    O -->|Orchestrates| P
    Q -->|Tracks metadata of| P[DBT]
    Q -->|Tracks metadata of| A
    P -->|Operates on| E
```

## MVP Roadmap

- [x] set up a mkdocs site to document the terrarium
- [x] add pre-commit checks to the project
- [x] set up a Makefile to make it easier to run the services and start the Terrarium, parts of the terrarium.
- [x] set up a project homepage using [Homepage](https://github.com/gethomepage/homepage) or something similar to make a
  single point of entry for all the services in the Terrarium.
- [x] Kafka Connectors
    - [PostgreSQL Sink](https://docs.confluent.io/cloud/current/connectors/cc-postgresql-sink.html)
    - [MongoDB Sink](https://www.mongodb.com/docs/kafka-connector/current/sink-connector/configuration-properties/all-properties/)
- [x] setup metabase with some default dashboards for the terrarium
- [x] implement DataHub to track metadata of the terrarium
- [ ] implement a DBT project to be orchestrated by airflow that does some operations on data within postgres
    - have it both generate and operate on data that it creates and uses and have it operate on datagen data being
      produced from kafka
- [ ] setup example python documentation examples to demonstrate interactions with the different services in the
  terrarium
- [ ] build out the airflow instance with DAG's that perform scheduled operations on the rest of the services in the
  terrarium
- [ ] implement openmetadata with the same setup as datahub
- [ ] create some endpoints in the FastAPI app that query topics using KSQL
- [ ] deploy a model using MLFlow and serve basic features to it from feast
    - deploy the model as a FastAPI app, and/or as an RPC service, that the main FastAPI app can interact with

## Long Term Goals

- [ ] explore using [arq](https://arq-docs.helpmanual.io/) for RPC
    - thinking of having the fastapi app be able to interact with another application (i.e. a model) using RPC with arq
    - or look at other options (celery, apscheduler, etc.) to get an example together for developing distributed apps.
- [ ] configure all exposed services to run through a Traefik load balancer
    - this would be a good exercise in setting up a reverse proxy and load balancer for the terrarium
- [ ] set up a Spark server and explore that more
    - follow the quick start guide to get a feel for it and operate on local files (testing parquet, csv, json, avro,
      etc.)
    - see about setting up apache iceberg locally and having Spark operate on it.
- [ ] configure to run everything on kubernetes with helm. the goal is to see if the whole stack can be deployed on 3
  raspberry pi's using k3s.
    - write docs and instructions on setting up the hardware
    - write docs and instructions on setting up the k3s cluster
    - write docs and instructions for deploying the stack on the cluster

## Projects to Keep an Eye On

- [FastUI](https://github.com/pydantic/FastUI): A new way to build web application user interfaces defined by
  declarative Python code... [read more about it here](https://docs.pydantic.dev/fastui/#the-principle)
