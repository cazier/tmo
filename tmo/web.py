import os

from fastapi import FastAPI

from tmo import Config, config

Config.from_file(os.environ["TMO_UVICORN_CONFIG_PATH"])

from .frontend import pages, static
from .frontend.pages import frontend

# ruff: noqa: E402
from .routers.api import api

app = FastAPI(debug=config.api.debug)
app.include_router(api)
app.include_router(frontend)
app.mount("/static", static, "static")

pages.app = app
