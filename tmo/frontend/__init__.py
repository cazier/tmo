import pathlib

from fastapi import staticfiles
from fastapi.templating import Jinja2Templates

from .. import config
from .filters import currency_class

static = staticfiles.StaticFiles(directory=pathlib.Path(__file__).parent.joinpath("static"))

templates = Jinja2Templates(directory=pathlib.Path(__file__).parent.joinpath("templates"))
templates.env.globals.update(domain="T-Mobile Bills", cdn=not config.api.debug)
templates.env.filters.update(currency_class=currency_class)

__all__ = ["static", "templates"]
