from fastapi import FastAPI

from tmo.config import api
from tmo.db.api import router as api_router
from tmo.render import router as web_router

app = FastAPI(debug=api["debug"])
app.include_router(api_router)
app.include_router(web_router)
