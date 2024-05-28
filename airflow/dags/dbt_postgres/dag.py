from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta


default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2023, 5, 1),
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}
# Create the DAG with the specified schedule interval
with DAG(
    "dbt_dag",
    default_args={
        "owner": "airflow",
        "depends_on_past": False,
        "start_date": datetime(2023, 5, 1),
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
    },
    schedule_interval=timedelta(days=1),
) as dag:
    # NOTE: this DBT run currently expects the kafka and postgres terrarium services to have been started and that the
    #       kafka datagen connector has loaded some data into the postgres database for this to operate on.
    # TODO: switch this back to the default starting DBT example code so that it doesn't depend on any outside data
    #       existing

    run_dbt_model = BashOperator(task_id="run_dbt_model", bash_command="dbt run")

    # TODO: add a task to run the datahub CLI DBT metadata ingestion after (and maybe before) the DBT run
