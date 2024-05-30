import typer

app = typer.Typer(no_args_is_help=True)


# TODO: can start creating commands here instead of using the makefile
#         - have it check to make sure dependencies are installed and available (docker and docker-compose)
#         - have it pull in information about all projects in the terrarium and dynamically make commands to start
#           and stop each
#         - give it some helper commands like `clean` to delete unused volumes and whatnot
@app.command()
def hello():
    print("Hello, Tech-Terrarium!")


@app.command()
def start(service: str):
    print(f"Starting {service}...")


if __name__ == "__main__":
    app()
