import datetime
import http
import pathlib
import typing

from fastapi import APIRouter, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from tmo import config

from ..dependencies import SessionDependency
from ..routers.bill import get_bill_id, get_previous_ids
from .filters import BillsRender, currency_class

templates = Jinja2Templates(directory=pathlib.Path(__file__).parent.joinpath("templates"))
templates.env.globals.update(domain="T-Mobile Bills", cdn=not config.api.debug)
templates.env.filters.update(currency_class=currency_class)

frontend = APIRouter(include_in_schema=False)
app: typing.Optional[FastAPI] = None


def _error_printer(code: int, request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "error.html.j2", {"status": http.HTTPStatus(code)}, code)


@frontend.get("/bill")
@frontend.get("/bill/{year}/{month}")
async def get_bill_pair(
    *, year: int | None = None, month: int | None = None, request: Request, session: SessionDependency
) -> HTMLResponse:
    if year and month:
        date = datetime.date(year, month, 1)
    else:
        date = datetime.date.today()

    current, previous = [
        await get_bill_id(id=id, session=session)
        for id in await get_previous_ids(before=date, count=2, session=session)
    ]

    render = BillsRender.model_validate({"month": date, "current": current, "previous": previous})

    return templates.TemplateResponse(request=request, name="bill.html.j2", context={"bill": render, "date": date})
