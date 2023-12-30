import datetime
import http
import pathlib
from typing import Any, Optional

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from httpx import AsyncClient

from tmo.db.api import router as api
from tmo.db.models import MonthValidator, keys

templates = Jinja2Templates(directory=pathlib.Path(__file__).parent.joinpath("templates"))
templates.env.globals.update(domain="T-Mobile Bills")

router = APIRouter(include_in_schema=False)


def _error_printer(code: int, request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "error.html.j2", {"status": http.HTTPStatus(code)}, code)


@router.get("/bill/", response_class=HTMLResponse)
@router.get("/bill/{year}/{month}", response_class=HTMLResponse)
async def homepage(*, year: Optional[int] = None, month: Optional[int] = None, request: Request):
    if year and month:
        date = datetime.date(year, month, 1)
    else:
        date = datetime.date.today()

    async with AsyncClient() as client:
        resp = await client.get(f"{request.base_url}{api.prefix[1:]}/month/{date.year}/{date.month}")

    if resp.status_code != 200:
        return _error_printer(resp.status_code, request)

    legend = keys()

    return templates.TemplateResponse(
        request=request, name="bill.html.j2", context={"bill": resp.json(), "date": date, "legend": legend}
    )
