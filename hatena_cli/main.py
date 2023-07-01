from typing import Optional
from typing_extensions import Annotated
from pathlib import Path
from rich import print
import typer

from .config import iter_config, get_config, set_config
from .api import upload_entry, update_entry, delete_entry
from . import __version__


app = typer.Typer()

config_app = typer.Typer()
app.add_typer(config_app, name="config")


def version_callback(value: bool):
    if value:
        print(f"Hatena Blog CLI Version: {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        Optional[bool],
        typer.Option(
            help="Show the CLI version.", callback=version_callback, is_eager=True
        ),
    ] = None,
):
    """
    Command line utility for Hatena Blog.
    """


@app.command()
def upload(
    blog_title: Annotated[str, typer.Argument(help="The title of the blog entry.")],
    blog_path: Annotated[
        Path, typer.Argument(help="The path of the blog entry (Markdown).")
    ],
    publish: Annotated[
        bool,
        typer.Option(help="Publish the blog entry if true.", prompt="Publish draft?"),
    ],
    with_images: Annotated[
        bool,
        typer.Option(help="Upload the images if true.", prompt="Upload images?"),
    ],
):
    """
    Upload a blog entry to Hatena Blog.

    Converts the given Markdown file to a HTML file and uploads it.
    Optionally uploads images in the Markdown to Hatena Fotolife,
    replacing image URLs in the HTML appropriately.
    """
    upload_entry(blog_title, blog_path, with_images, publish)


@app.command()
def update(
    blog_title: Annotated[str, typer.Argument(help="The title of the blog entry.")],
    blog_path: Annotated[
        Path,
        typer.Argument(help="The path of the blog entry (Markdown)."),
    ],
    blog_id: Annotated[int, typer.Argument(help="The id of the blog entry.")],
    publish: Annotated[
        bool,
        typer.Option(help="Publish the blog entry if true.", prompt="Publish draft?"),
    ],
    with_images: Annotated[
        bool, typer.Option(help="Update the images if true.", prompt="Upload images?")
    ],
):
    """
    Update a Hatena Blog entry by blog ID.

    Converts the given Markdown to HTML and updates it.
    Optionally uploads images in the Markdown to Hatena Fotolife,
    replacing image URLs in the HTML appropriately.
    Previously uploaded images are deleted from Hatena Fotolife.
    The URLs for these images are found by downloading the HTML from Hatena Blog.
    """
    update_entry(blog_id, blog_title, blog_path, with_images, publish)


@app.command()
def delete(
    blog_id: Annotated[int, typer.Argument(help="The id of the blog entry.")],
    with_images: Annotated[
        bool, typer.Option(help="Delete the images if true.", prompt="Delete images?")
    ],
):
    """
    Delete a Hatena Blog entry by blod ID.

    Opitionally deletes uploaded images from Hatena Fotolife.
    The URLs for these images are found by downloading the HTML from Hatena Blog.
    """
    print(f"This command will delete blog entry {blog_id}.")
    typer.confirm("Continue?", abort=True)
    delete_entry(blog_id, with_images)


@config_app.callback()
def config():
    """
    Manage the CLI configuration.
    """
    pass


@config_app.command("init")
def config_init():
    """
    Initialise the CLI configuration interactively.
    """
    for key in ["auth:api_key", "auth:api_secret", "blog:username", "blog:domain"]:
        value = typer.prompt(key)
        set_config(key, value)


@config_app.command("list")
def config_list():
    """
    List the CLI configuration.
    """
    print("List of config:")
    for key, value in iter_config():
        print(f"{key}: {value}")


@config_app.command("get")
def config_get(
    key: Annotated[str, typer.Argument(help="The key of the CLI configuration.")]
):
    """
    Get the CLI configuration by the given key.
    """
    print(f"{key}: {get_config(key)}")


@config_app.command("set")
def config_set(
    key: Annotated[str, typer.Argument(help="The key of the CLI configuration.")],
    value: Annotated[
        str,
        typer.Argument(help="The value of the CLI configuration."),
    ],
):
    """
    Set the CLI configuration by the given key.
    """
    set_config(key, value)
    print(f"{key}: {value}")


if __name__ == "__main__":
    app()
