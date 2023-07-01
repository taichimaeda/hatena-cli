from .main import app

# Makes the CLI callable from `python -m`.
# https://typer.tiangolo.com/tutorial/package/#support-python-m-optional
app(prog_name="hatena-cli")
