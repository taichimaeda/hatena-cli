import os
import base64
import re
import requests
from urllib import parse
from pathlib import Path
from requests_oauthlib import OAuth1
from bs4 import BeautifulSoup
from rich import print

import typer

from .cli import ProgressBar, Spinner
from .auth import get_auth
from .config import get_config


_HATENA_BLOG_URL = f"https://blog.hatena.ne.jp"
_HATENA_FOTOLIFE_POST_URL = "https://f.hatena.ne.jp/atom/post"
_HATENA_FOTOLIFE_EDIT_URL = "https://f.hatena.ne.jp/atom/edit"


def _convert(blog_path: Path = None):
    with Spinner() as progress:
        progress.add_task("Converting Markdown to HTML...")

        pandoc_path = get_config("path:pandoc")
        template_path = get_config("path:template")
        os.system(
            f"{pandoc_path} --quiet --standalone --template '{template_path}' \
                            --output '{blog_path.with_suffix('.html')}' '{blog_path}'"
        )


def upload_entry(blog_title: str, blog_path: Path, with_images: bool, publish: bool):
    _convert(blog_path)
    auth = get_auth()
    if with_images:
        _upload_images(blog_title, blog_path, auth)
    _upload_html(blog_title, blog_path, publish, auth)


def _upload_images(blog_title: str, blog_path: Path, auth: OAuth1):
    with ProgressBar() as progress:
        image_pattern = get_config("image:pattern")
        image_replace = get_config("image:replace")
        with open(blog_path.with_suffix(".html"), mode="r") as file:
            content = file.read()

        total = len(re.findall(image_pattern, content))
        task = progress.add_task("Uploading images...", total=total)

        def callback(match: re.Match):
            image_path = parse.unquote(match.group(1))
            image_url = _upload_image(blog_title, image_path, auth)
            progress.advance(task, 1)
            return image_replace.replace(r"\1", image_url)

        content = re.sub(image_pattern, callback, content)
        with open(blog_path.with_suffix(".html"), mode="w") as file:
            file.write(content)


def _upload_image(blog_title: str, image_path: Path, auth: OAuth1) -> str:
    with open(image_path, mode="rb") as file:
        content = file.read()
        content = base64.b64encode(content).decode()

    # Maximum length for <dc:subject /> is 24
    res = requests.post(
        _HATENA_FOTOLIFE_POST_URL,
        auth=auth,
        timeout=None,
        headers={"Content-Type": "application/xml"},
        data=f"""\
<?xml version="1.0"?>
<entry xmlns="http://purl.org/atom/ns#">
    <dc:subject>{blog_title[:24]}</dc:subject>
    <title>{blog_title}</title>
    <content mode="base64" type="image/png">{content}</content>
</entry>""",
    )

    if res.status_code != 201:
        print("[red]Error while uploading image.")
        raise typer.Abort()

    xml = BeautifulSoup(res.text, features="xml")
    url = xml.find("entry").find("hatena:imageurl").text
    return url


def _upload_html(blog_title: str, blog_path: Path, publish: bool, auth: OAuth1):
    with Spinner() as progress:
        progress.add_task("Uploading HTML...")

        with open(blog_path.with_suffix(".html"), mode="r") as file:
            content = file.read()

        username = get_config("blog:username")
        domain = get_config("blog:domain")
        res = requests.post(
            f"{_HATENA_BLOG_URL}/{username}/{domain}/atom/entry",
            auth=auth,
            timeout=None,
            headers={"Content-Type": "application/xml; charset=utf-8"},
            data=f"""\
<?xml version="1.0" encoding="utf-8"?>
<entry xmlns="http://www.w3.org/2005/Atom" xmlns:app="http://www.w3.org/2007/app">
    <title>{blog_title}</title>
    <author><name>name</name></author>
    <content type="text/html"><![CDATA[{content}]]></content>
    <app:control><app:draft>{'no' if publish else 'yes'}</app:draft></app:control>
</entry>""".encode(
                "utf-8"
            ),
        )

        if res.status_code != 201:
            print("[red]Error while uploading HTML.")
            raise typer.Abort()


def update_entry(
    blog_id: int, blog_title: str, blog_path: Path, with_images: bool, publish: bool
):
    _convert(blog_path)
    auth = get_auth()
    if with_images:
        _update_images(blog_id, blog_title, blog_path, auth)
    _update_html(blog_id, blog_title, blog_path, publish, auth)


def _update_images(blog_id: int, blog_title: str, blog_path: Path, auth: OAuth1):
    _delete_images(blog_id, auth)
    _upload_images(blog_title, blog_path, auth)


def _update_html(
    blog_id: int, blog_title: str, blog_path: Path, publish: bool, auth: OAuth1
):
    with Spinner() as progress:
        progress.add_task("Updating HTML...")

        with open(blog_path.with_suffix(".html"), mode="r") as file:
            content = file.read()

        username = get_config("blog:username")
        domain = get_config("blog:domain")
        res = requests.put(
            f"{_HATENA_BLOG_URL}/{username}/{domain}/atom/entry/{blog_id}",
            auth=auth,
            timeout=None,
            headers={"Content-Type": "application/xml; charset=utf-8"},
            data=f"""\
<?xml version="1.0" encoding="utf-8"?>
<entry xmlns="http://www.w3.org/2005/Atom" xmlns:app="http://www.w3.org/2007/app">
    <title>{blog_title}</title>
    <author><name>name</name></author>
    <content type="text/html"><![CDATA[{content}]]></content>
    <app:control><app:draft>{'no' if publish else 'yes'}</app:draft></app:control>
</entry>""".encode(
                "utf-8"
            ),
        )

        if res.status_code != 200:
            print("[red]Error while updating HTML.")
            raise typer.Abort()


def delete_entry(blog_id: int, with_images: bool):
    auth = get_auth()
    if with_images:
        _delete_images(blog_id, auth)
    _delete_html(blog_id, auth)


def _delete_images(blog_id: int, auth: OAuth1):
    with ProgressBar() as progress:
        username = get_config("blog:username")
        domain = get_config("blog:domain")
        res = requests.get(
            f"{_HATENA_BLOG_URL}/{username}/{domain}/atom/entry/{blog_id}",
            auth=auth,
            timeout=None,
        )

        if res.status_code != 200:
            print("[red]Error while downloading HTML.")
            raise typer.Abort()

        xml = BeautifulSoup(res.text, features="xml")
        content = xml.find("entry").find("hatena:formatted-content").text
        content = parse.unquote(content)

        image_pattern = get_config("image:pattern")
        total = len(re.findall(image_pattern, content))
        task = progress.add_task("Deleting images...", total=total)

        def callback(match: re.Match):
            image_path = parse.unquote(match.group(1))
            image_id = os.path.splitext(os.path.basename(image_path))[0]
            res = requests.delete(
                f"{_HATENA_FOTOLIFE_EDIT_URL}/{image_id}", auth=auth, timeout=None
            )
            if res.status_code != 200:
                print("[red]Error while deleting image.")
                raise typer.Abort()
            progress.advance(task, 1)

        re.sub(image_pattern, callback, content)


def _delete_html(blog_id: int, auth: OAuth1):
    with Spinner() as progress:
        progress.add_task("Deleting HTML...")

        username = get_config("blog:username")
        domain = get_config("blog:domain")
        res = requests.delete(
            f"{_HATENA_BLOG_URL}/{username}/{domain}/atom/entry/{blog_id}",
            auth=auth,
            timeout=None,
        )

        if res.status_code != 200:
            print("[red]Error while deleting HTML.")
            raise typer.Abort()
