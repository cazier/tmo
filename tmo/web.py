import os

from fastapi import FastAPI

from tmo import Config, config

Config.from_file(os.environ["TMO_UVICORN_CONFIG_PATH"])

# pylint: disable=wrong-import-position
from tmo.db.api import router as api_router
from tmo.frontend import router as web_router
from tmo.frontend import static

app = FastAPI(debug=config.api.debug)
app.include_router(api_router)
app.include_router(web_router)
app.mount("/static", static, "static")
