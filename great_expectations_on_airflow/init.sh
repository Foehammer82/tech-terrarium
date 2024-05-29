#!/bin/bash

airflow connections add 'postgres_default' \
    --conn-type 'postgres' \
    --conn-login 'postgres' \
    --conn-password 'password' \
    --conn-host 'postgres' \
    --conn-port 5432;

airflow connections add 'mongo_default' \
    --conn-type 'mongo' \
    --conn-login 'admin' \
    --conn-password 'password' \
    --conn-host 'mongo' \
    --conn-port 27017;

airflow connections add 'kafka_default' \
    --conn-type 'kafka' \
    --conn-extra '{"bootstrap.servers": "broker:9092"}';