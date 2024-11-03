import os

from fastapi import FastAPI

from tmo import Config, config

Config.from_file(os.environ["TMO_UVICORN_CONFIG_PATH"])

# ruff: noqa: E402
from tmo.routers.api import api
from tmo.frontend.pages import frontend
from tmo.frontend import static

app = FastAPI(debug=config.api.debug)
app.include_router(api)
app.include_router(frontend)
app.mount("/static", static, "static")
