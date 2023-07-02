import toml
from flatdict import FlatDict
from pathlib import Path
from datetime import datetime
from rich import print
import typer


class _Config(FlatDict):
    def __getitem__(self, key: any):
        try:
            return super().__getitem__(key)
        except KeyError:
            print(f"[red]Config {key} not found.")
            typer.Abort()


_APP_DIR = Path(typer.get_app_dir("hatena-cli"))
_CONFIG_PATH = _APP_DIR / "config.toml"
_TEMPLATE_PATH = _APP_DIR / "template.html"
_PANDOC_PATH = Path("/opt/homebrew/bin/pandoc")
_DEFAULT_CONFIG = _Config(
    {
        "auth": {
            "api_key": "",
            "api_secret": "",
            "access_token": "",
            "access_secret": "",
            "expires": datetime.now(),
        },
        "blog": {
            "username": "",
            "domain": "",
        },
        "image": {
            "pattern": r'src="(.+\.(?:jpg|png))"',
            "replace": r'src="\1"',
        },
        "path": {
            "template": _TEMPLATE_PATH.as_posix(),
            "pandoc": _PANDOC_PATH.as_posix(),
        },
    }
)
_DEFAULT_TEMPLATE = "$body$"


_config = _Config(toml.load(_CONFIG_PATH))


def check_config():
    if not _APP_DIR.exists():
        _APP_DIR.mkdir(parents=True, exist_ok=True)
    if not _CONFIG_PATH.exists():
        with open(_CONFIG_PATH, "w") as file:
            toml.dump(_DEFAULT_CONFIG.as_dict(), file)
    if not _TEMPLATE_PATH.exists():
        with open(_TEMPLATE_PATH, "w") as file:
            file.write(_DEFAULT_TEMPLATE)

    global _config
    if _config is None:
        _config = _Config(toml.load(_CONFIG_PATH))


def iter_config() -> any:
    check_config()

    global _config
    return _config.iteritems()


def get_config(key: str) -> any:
    check_config()

    global _config
    return _config[key]


def set_config(key: str, value: any):
    check_config()

    global _config
    _config[key] = value

    with open(_CONFIG_PATH, "w") as file:
        toml.dump(_config.as_dict(), file)
