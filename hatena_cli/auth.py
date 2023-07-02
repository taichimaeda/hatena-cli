from typing import Tuple
from urllib import parse
from datetime import datetime, timedelta
from requests_oauthlib import OAuth1
import requests
import typer

from .cli import Spinner
from .config import get_config, set_config


_HATENA_SCOPES = ["read_public", "write_public", "read_private", "write_private"]
_HATENA_INITIATE_URL = "https://www.hatena.com/oauth/initiate"
_HATENA_AUTHORIZE_URL = "https://www.hatena.ne.jp/oauth/authorize"
_HATENA_ACCESS_TOKEN_URL = "https://www.hatena.com/oauth/token"


def get_auth() -> OAuth1:
    check_auth()
    return OAuth1(
        get_config("auth:api_key"),
        get_config("auth:api_secret"),
        get_config("auth:access_token"),
        get_config("auth:access_secret"),
    )


def check_auth():
    access_token = get_config("auth:access_token")
    access_secret = get_config("auth:access_secret")
    expires = get_config("auth:expires")
    api_key = get_config("auth:api_key")
    api_secret = get_config("auth:api_secret")

    if access_token == "" or access_secret == "" or datetime.now() >= expires:
        access_token, access_secret = _get_access_token(api_key, api_secret)
        expires = datetime.now() + timedelta(days=60)

    set_config("auth:access_token", access_token)
    set_config("auth:access_secret", access_secret)
    set_config("auth:expires", expires)


def _get_access_token(api_key: str, api_secret: str) -> Tuple[str, str]:
    request_token, request_secret = _get_request_token(api_key, api_secret)
    verifier = _get_verifier(request_token)

    with Spinner() as progress:
        progress.add_task("Obtaining access token...")

        auth = OAuth1(
            api_key, api_secret, request_token, request_secret, verifier=verifier
        )
        res = requests.post(_HATENA_ACCESS_TOKEN_URL, auth=auth)
        params = dict(parse.parse_qsl(res.text))
        access_token = params["oauth_token"]
        access_secret = params["oauth_token_secret"]
        return (access_token, access_secret)


def _get_request_token(api_key: str, api_secret: str) -> Tuple[str, str]:
    with Spinner() as progress:
        progress.add_task("Obtaining request token...")

        auth = OAuth1(api_key, api_secret, callback_uri="oob")
        res = requests.post(
            _HATENA_INITIATE_URL, auth=auth, data={"scope": ",".join(_HATENA_SCOPES)}
        )
        params = dict(parse.parse_qsl(res.text))
        request_token = params["oauth_token"]
        request_secret = params["oauth_token_secret"]
        return (request_token, request_secret)


def _get_verifier(request_token: str) -> str:
    with Spinner() as progress:
        progress.add_task("Launching web browser for user authentication...")

        typer.launch(f"{_HATENA_AUTHORIZE_URL}?oauth_token={request_token}")

    verifier = typer.prompt("Enter code")
    return verifier
