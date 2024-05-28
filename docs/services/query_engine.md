# Query Engine

## Spark

Apache Spark is an open-source, distributed computing system used for big data processing and analytics. It provides an
interface for programming entire clusters with implicit data parallelism and fault tolerance. It can handle both batch
and real-time analytics and data processing workloads.

Spark supports multiple programming languages such as Java, Python, and Scala and comes with built-in modules for SQL,
streaming, machine learning, and graph processing. It can be run on Hadoop, standalone, or in the cloud and can access
diverse data sources including HDFS, Cassandra, HBase, and S3.

## Scrubbed Services

### Trino

It ended up being more effort to implement than i expected. I think it's a great tool, but for the purposes of this
project, it was overkill. I would recommend it for larger projects where you need to query multiple data sources, or
need to query data in a distributed manner. May come back to it in the future, but for now, it's on the shelf.