# Great Expectations

[Great Expectations Docs](https://docs.greatexpectations.io/docs/home/?banner=false)

## Notes:

- need a clean way to build and organize expectations (likely with json to match what GX already does) (make sure docs
  reference or pull in all available expectations and have docs on how to make custom ones)
- setup postgres for validation results store (for detailed results and analytical usage later, will need to have a way
  to pipe to snowflake)
- tied into DH
- CI/CD to run functional tests that validate expectation configs (check tables and columns exist, connections to db is
  good, etc.)
  orchestrated with airflow. however, i think it would be really nice if that part was just abstracted away from the
  user and the gx workflow was to make and edit json files, tooling or cli commands to test/run localy, and then cicd to
  protect mistakes or bad expectations from getting deployed
