import http
import os

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from starlette.exceptions import HTTPException

from . import Config, config
from .frontend import static, templates
from .frontend.pages import frontend
from .routers.api import api
from .web2.exceptions import APIException

Config.from_file(os.environ["TMO_UVICORN_CONFIG_PATH"])

app = FastAPI(debug=config.api.debug)
app.include_router(api)
app.include_router(frontend)
app.mount("/static", static, "static")


@app.exception_handler(APIException)
def api_exception(_: Request, exc: APIException) -> JSONResponse:
    return JSONResponse({"detail": exc.detail}, status_code=exc.status_code)


@app.exception_handler(HTTPException)
def error_printer(request: Request, code: HTTPException) -> HTMLResponse:
    return templates.TemplateResponse(
        request, "error.html.j2", {"status": http.HTTPStatus(code.status_code)}, code.status_code
    )
