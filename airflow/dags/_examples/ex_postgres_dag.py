from datetime import datetime

from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from faker import Faker

fake = Faker()

with DAG(
    dag_id="ex_postgres_dag",
    start_date=datetime(2020, 2, 2),
    schedule=None,
    catchup=False,
) as dag:
    create_pet_table = PostgresOperator(
        task_id="create_pet_table",
        sql="""
            CREATE TABLE IF NOT EXISTS postgres.public.pet (
            pet_id SERIAL PRIMARY KEY,
            name VARCHAR NOT NULL,
            pet_type VARCHAR NOT NULL,
            birth_date DATE NOT NULL,
            OWNER VARCHAR NOT NULL);
          """,
    )

    insert_pet_data = PostgresOperator(
        task_id="insert_pet_data",
        sql=f"""
            INSERT INTO postgres.public.pet (name, pet_type, birth_date, owner)
            VALUES ('{fake.first_name()}', 'Dog', '{fake.date()}', '{fake.name()}');
          """,
        doc=(
            "NOTE: It is important to provide the full path to the table in order for lineage data to be properly "
            "captured"
        ),
    )

    create_pet_table >> insert_pet_data
