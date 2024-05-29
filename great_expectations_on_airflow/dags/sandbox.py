from pathlib import Path

import yaml
from great_expectations.core import ExpectationConfiguration
from great_expectations.data_context import FileDataContext
from great_expectations.datasource import Datasource

"""
For this to be successful, we must be able to create expectation DAG's easily by defining:
- the database we are running the expectations on (as an airflow connection id)

then tasks should should take in:
- table name
- the expectations to run on the table (which can be looked up from the expectations catalog (https://greatexpectations.io/expectations/)

THAT'S IT! that is how the user experience needs to be.  My goal is to create a function that will take those values in
leveraging pydantic models so that we can make it easy to see what expectations are doing and how they are configured 
without any risk of getting lost in the massive, MASSIVE, spaghetti code that is the great expectations codebase.
"""

if __name__ == "__main__":
    root_dir = Path("./include").absolute()

    # https://docs.greatexpectations.io/docs/oss/guides/setup/configuring_data_contexts/instantiating_data_contexts/instantiate_data_context#create-a-context
    context = FileDataContext.create(project_root_dir=root_dir.as_posix())
    print(context)

    # Add datasources
    datasource_config = {
        "name": "my_postgres_datasource",
        "class_name": "Datasource",
        "execution_engine": {
            "class_name": "SqlAlchemyExecutionEngine",
            "connection_string": "postgresql+psycopg2://postgres:password@localhost:5432/postgres",
        },
        "data_connectors": {
            "default_runtime_data_connector_name": {
                "class_name": "RuntimeDataConnector",
                "batch_identifiers": ["default_identifier_name"],
            },
            "default_inferred_data_connector_name": {
                "class_name": "InferredAssetSqlDataConnector",
                "include_schema_name": True,
            },
        },
    }
    context.test_yaml_config(yaml.dump(datasource_config))
    context.add_datasource(**datasource_config)
    pg_datasource: Datasource = context.get_datasource("my_postgres_datasource")

    # https://docs.greatexpectations.io/docs/oss/guides/expectations/how_to_create_and_edit_expectations_based_on_domain_knowledge_without_inspecting_data_directly#create-an-expectationsuite
    suite = context.add_or_update_expectation_suite(expectation_suite_name="my_suite")

    # Create an Expectation
    expectation_configuration_1 = ExpectationConfiguration(
        # Name of expectation type being added
        expectation_type="expect_table_columns_to_match_ordered_list",
        # These are the arguments of the expectation
        # The keys allowed in the dictionary are Parameters and
        # Keyword Arguments of this Expectation Type
        kwargs={
            "column_list": [
                "pet_id",
                "name",
                "pet_type",
                "birth_date",
                "owner",
            ]
        },
        # This is how you can optionally add a comment about this expectation.
        # It will be rendered in Data Docs.
        # See this guide for details:
        # `How to add comments to Expectations and display them in Data Docs`.
        meta={
            "notes": {
                "format": "markdown",
                "content": "Some clever comment about this expectation. **Markdown** `Supported`",
            }
        },
    )
    # Add the Expectation to the suite
    suite.add_expectation(expectation_configuration=expectation_configuration_1)

    # Save the suite
    context.save_expectation_suite(expectation_suite=suite)

    # define the data asset to test
    # https://docs.greatexpectations.io/docs/oss/guides/connecting_to_your_data/fluent/database/connect_sql_source_data?sql-database-type=postgresql#connect-a-data-asset-to-the-data-in-a-table-optional
    # table_asset = pg_datasource  .add_table_asset(
    #     name="my_pet_table_asset",
    #     table_name="postgres.public.pet",
    # )

    # get a checkpoint
    checkpoint = context.add_or_update_checkpoint(
        name="my_checkpoint",
        validations=[
            {
                "batch_request": {
                    "datasource_name": pg_datasource.name,
                    "data_connector_name": "default_runtime_data_connector_name",
                    "data_asset_name": "default_inferred_data_connector_name",
                    "data_connector_query": {"index": -1},
                },
                "expectation_suite_name": suite.name,
            },
        ],
        action_list=[
            {
                "name": "datahub_action",
                "action": {
                    "module_name": "datahub.integrations.great_expectations.action",
                    "class_name": "DataHubValidationAction",
                    "server_url": "http://localhost:8089",
                },
            }
        ],
    )

    # run the checkpoint
    checkpoint_result = checkpoint.run()

    # create the datadocs for the dcheckpoint
    context.build_data_docs()
