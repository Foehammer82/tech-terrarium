# Diagrams

```mermaid
graph LR
    A[FastAPI] -->|Interacts with| B[Redis]
    A -->|Interacts with| C[gRPC Service]
    A -->|Interacts with| D[Kafka]
    D -->|Interacts with| E[PostgreSQL Sink]
    D -->|Interacts with| F[GitHub Source]
    D -->|Interacts with| G[Flink]
    D -->|Interacts with| H[Spark]
    I[MongoDB] -->|Interacts with| J[Mongo Express]
    K[Metabase] -->|Interacts with| L[PostgreSQL]
    M[InfluxDB] -->|Monitors| N[Terrarium Services]
    O[Airflow] -->|Orchestrates| P[DBT]
    Q[DataHub] -->|Tracks metadata of| R[Terrarium Services]
    S[OpenMetadata] -->|Tracks metadata of| R
    T[MlFlow] -->|Builds and releases models| U[Feast]
    V[Homepage] -->|Single point of entry for| R
```

In this diagram:

- FastAPI interacts with Redis, gRPC Service, and Kafka.
- Kafka interacts with PostgreSQL Sink, GitHub Source, Flink, and Spark.
- MongoDB interacts with Mongo Express.
- Metabase interacts with PostgreSQL.
- InfluxDB monitors all the services in the Terrarium.
- Airflow orchestrates DBT.
- DataHub and OpenMetadata track metadata of all the services in the Terrarium.
- MlFlow builds and releases models with Feast.
- Homepage serves as a single point of entry for all the services in the Terrarium.

Please note that this is a basic diagram and the actual interactions might be more complex depending on the specific
implementation of each service.