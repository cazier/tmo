import http
import pathlib

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from tmo import config

# from tmo.db.api import router as api
from tmo.frontend.filters import currency_class

templates = Jinja2Templates(directory=pathlib.Path(__file__).parent.joinpath("templates"))
templates.env.globals.update(domain="T-Mobile Bills", cdn=not config.api.debug)
templates.env.filters.update(currency_class=currency_class)

frontend = APIRouter(include_in_schema=False)


def _error_printer(code: int, request: Request) -> HTMLResponse:
    return templates.TemplateResponse(request, "error.html.j2", {"status": http.HTTPStatus(code)}, code)


@frontend.get("/bill")
@frontend.get("/bill/{year}/{month}")
async def bill(*, year: Optional[int] = None, month: Optional[int] = None, request: Request) -> HTMLResponse:
    if year and month:
        date = datetime.date(year, month, 1)
    else:
        date = datetime.date.today()

    base_url = f"{request.base_url}{api.prefix[1:]}"

    async with AsyncClient() as client:
        resp = await client.get(f"{base_url}/render/{date.year}/{date.month}")

    if resp.status_code != 200:
        return _error_printer(resp.status_code, request)

    current, previous = resp.json()

    render = BillsRender.model_validate({"month": date, "current": current, "previous": previous})

    return templates.TemplateResponse(request=request, name="bill.html.j2", context={"bill": render, "date": date})
