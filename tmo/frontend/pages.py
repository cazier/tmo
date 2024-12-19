import datetime

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from httpx import ASGITransport, AsyncClient, Response

from . import templates
from .filters import BillsRender

frontend = APIRouter(include_in_schema=False)


@frontend.get("/bill")
@frontend.get("/bill/{year}/{month}")
async def get_bill_pair(*, year: int | None = None, month: int | None = None, request: Request) -> HTMLResponse:
    async def _get_bill(id: int, client: AsyncClient) -> Response:
        url = request.url_for("get_bill_detailed", id=id)

        return await client.get(f"{client.base_url!s}{url.path}")

    if year and month:
        date = datetime.date(year, month, 1)
    else:
        date = datetime.date.today()

    ids_url = request.url_for("get_previous_ids")

    async with AsyncClient(transport=ASGITransport(app=request.app), base_url="http://app.internal") as client:
        ids = await client.get(f"http://app.internal{ids_url.path}", params={"before": date.isoformat(), "count": 2})
        current, previous = [(await _get_bill(id, client)).json() for id in ids.json()]

    render = BillsRender.model_validate({"month": date, "current": current, "previous": previous})

    return templates.TemplateResponse(request=request, name="bill.html.j2", context={"bill": render, "date": date})
