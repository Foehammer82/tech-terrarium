# Great Expectations

working on getting this implemented to play nice with DataHub, run in an airflow instance, and all-around just work has
been a challenge to say the least. I'm almost hesitant to keep going, but there aren't many other options out there
for data validation tooling like this. And based on looking through the source code i think what we have what we need
to make this successful.

If we can get this working, it might be worth considering building and releasing it as a plugin for Airflow to make it
easier to integrate in future projects.

## Notes:

For this to be successful in airflow, we must be able to create expectation DAG's easily by defining:

- the database we are running the expectations on (as an airflow connection id)

then tasks should take in:

- table name
- the expectations to run on the table (which can be looked up from the expectations
  catalog (https://greatexpectations.io/expectations/)

THAT'S IT! that is how the user experience needs to be. My goal is to create a function that will take those values in
leveraging pydantic models so that we can make it easy to see what expectations are doing and how they are configured
without any risk of getting lost in the massive, MASSIVE, spaghetti code that is the great expectations codebase.