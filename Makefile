start-all: start-admin start-kafka start-postgres start-mongo start-fastapi-app start-airflow start-metabase start-datahub
stop-all: stop-admin stop-kafka stop-postgres stop-mongo stop-fastapi-app stop-airflow stop-metabase stop-datahub

# Clean up
cleanup:
	docker system prune -a -f

# Admin
start-admin:
	docker-compose -f admin/docker-compose.yaml -p admin up -d --force-recreate
stop-admin:
	docker-compose -f admin/docker-compose.yaml -p admin down

# Kafka
start-kafka:
	docker-compose -f kafka/docker-compose.yaml -p kafka up -d --force-recreate
stop-kafka:
	docker-compose -f kafka/docker-compose.yaml -p kafka down

# Postgres
start-postgres:
	docker-compose -f postgres/docker-compose.yaml -p postgres up -d --force-recreate
stop-postgres:
	docker-compose -f postgres/docker-compose.yaml -p postgres down

# Mongo
start-mongo:
	docker-compose -f mongo/docker-compose.yaml -p mongo up -d --force-recreate
stop-mongo:
	docker-compose -f mongo/docker-compose.yaml -p mongo down

# FastAPI App
start-fastapi-app:
	docker-compose -f fastapi_app/docker-compose.yaml -p fastapi-app up -d --force-recreate
stop-fastapi-app:
	docker-compose -f fastapi_app/docker-compose.yaml -p fastapi-app down

# Airflow
start-airflow:
	docker-compose -f airflow/docker-compose.yaml -p airflow up -d --force-recreate
stop-airflow:
	docker-compose -f airflow/docker-compose.yaml -p airflow down

# Metabase
start-metabase:
	docker-compose -f metabase/docker-compose.yaml -p metabase up -d --force-recreate
stop-metabase:
	docker-compose -f metabase/docker-compose.yaml -p metabase down

# Datahub
start-datahub:
	docker-compose -f datahub/docker-compose.yaml -p datahub up -d --force-recreate
stop-datahub:
	docker-compose -f datahub/docker-compose.yaml -p datahub down
