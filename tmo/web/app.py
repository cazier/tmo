import http
import os

import fastapi
from starlette.exceptions import HTTPException

from .. import Config, config
from .exceptions import APIException
from .frontend import static, templates
from .frontend.pages import frontend
from .routers.api import api

Config.from_file(os.environ["TMO_UVICORN_CONFIG_PATH"])

app = fastapi.FastAPI(debug=config.api.debug)
app.include_router(api)
app.include_router(frontend)
app.mount("/static", static, "static")


@app.exception_handler(APIException)
def api_exception(_: fastapi.Request, exc: APIException) -> fastapi.responses.JSONResponse:
    return fastapi.responses.JSONResponse({"detail": exc.detail}, status_code=exc.status_code)


@app.exception_handler(HTTPException)
def error_printer(request: fastapi.Request, code: HTTPException) -> fastapi.responses.HTMLResponse:
    return templates.TemplateResponse(
        request, "error.html.j2", {"status": http.HTTPStatus(code.status_code)}, code.status_code
    )
