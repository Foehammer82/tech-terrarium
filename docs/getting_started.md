# Getting Started

## System Requirements

- **CPU**: at least 2 cores (4+ recommended)
- **RAM**: at least 16GB (32GB+ recommended)
- **Storage**: at least 64GB

## Prerequisites

This project assumes you have some basic knowledge of; git, docker, docker-compose, python, and SQL. However, if your
objective is to learn these technologies, this project is a great way to get started.

You will need to install:

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [Python](https://www.python.org/downloads/) (recommend 3.11)
- [Poetry](https://python-poetry.org/docs/)

### Setup Python Environment

1. Install Dependencies

    ```bash
    poetry install --no-root
    ```
2. Setup Pre-Commit (optional)
    - If you plan to fork or contribute to this project, it is recommended to set up pre-commit hooks.
    - One of the pre-commit hooks automates keeping the project working correctly by exporting the poetry lock file
      whenever the pyproject.toml file changes.

    ```bash
    poetry run pre-commit install
    ```

### First Steps

> TODO: build up the CLI app and then reference accessing it here

information about all terrarium-admin CLI commands can be accessed by running:

```bash
poetry run admin --help
```

1. Start the `admin` services
2. once that the services are up, open your browser and navigate to [http://localhost](http://localhost). you'll be
   greeted with the Terrarium homepage that shows all the services available to you. though only the admin services are
   running at this point.

3. Start the services you'd like to use/explore/observe
4. And that's it! you're ready to start exploring the Terrarium.
5. When you are done, you can stop all the services with:
6. To clean everything up after you've shut down the services, you can run:

## Next Steps

Now that you have the Terrarium up and running, you can start exploring the services and how they interact with each
other. The Terrarium homepage is a great place to start as it provides a single point of entry to all the services in
the
Terrarium.

You can find detailed information about each service, what it is, how to interact with it, etc. in
the [services](https://foehammer82.github.io/tech-terrarium/services/) section of the docs.
