import datetime
import http
import pathlib
import typing

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from httpx import AsyncClient

from tmo.config import api as config
from tmo.db.api import router as api
from tmo.frontend.filters import currency_class, previous, table

templates = Jinja2Templates(directory=pathlib.Path(__file__).parent.joinpath("templates"))
templates.env.globals.update(domain="T-Mobile Bills", cdn=not config["debug"])
templates.env.filters.update(currency_class=currency_class)

router = APIRouter(include_in_schema=False)


def _error_printer(code: int, request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "error.html.j2", {"status": http.HTTPStatus(code)}, code)


def _subtract_month(date: datetime.date) -> datetime.date:
    if date.month == 1:
        return datetime.date(date.year - 1, 12, 1)

    return datetime.date(date.year, date.month - 1, 1)


@router.get("/bill/")
@router.get("/bill/{year}/{month}")
async def homepage(
    *, year: typing.Optional[int] = None, month: typing.Optional[int] = None, request: Request
) -> HTMLResponse:
    if year and month:
        date = datetime.date(year, month, 1)
    else:
        date = datetime.date.today()

    previous_date = _subtract_month(date)

    base_url = f"{request.base_url}{api.prefix[1:]}/month"

    async with AsyncClient() as client:
        resp = await client.get(f"{base_url}/{date.year}/{date.month}")
        last = await client.get(f"{base_url}/{previous_date.year}/{previous_date.month}")

    if resp.status_code != 200:
        return _error_printer(resp.status_code, request)

    if last.status_code != 200:
        return _error_printer(last.status_code, request)

    last_totals = previous(last.json()["subscribers"])
    data = table((bill := resp.json()).pop("subscribers"))

    return templates.TemplateResponse(
        request=request, name="bill.html.j2", context={"bill": bill, "table": data, "date": date, "last": last_totals}
    )
