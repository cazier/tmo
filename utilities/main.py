import datetime
from typing import Generator, Optional

from fastapi import Depends, FastAPI
from pydantic import BaseModel

app = FastAPI()


class DB:
    table = {
        0: {"date": "2023-01-01", "day": "Sunday"},
        1: {"date": "2023-02-01", "day": "Wednesday"},
        2: {"date": "2023-03-01", "day": "Wednesday"},
        3: {"date": "2023-04-01", "day": "Saturday"},
        4: {"date": "2023-05-01", "day": "Monday"},
        5: {"date": "2023-06-01", "day": "Thursday"},
        6: {"date": "2023-07-01", "day": "Saturday"},
        7: {"date": "2023-08-01", "day": "Tuesday"},
        8: {"date": "2023-09-01", "day": "Friday"},
        9: {"date": "2023-10-01", "day": "Sunday"},
    }

    def get_id_by_date(self, year: int, month: int) -> int:
        for id, data in self.table.items():
            if data["date"] == f"{year}-{month:02}-01":
                return id

        raise Exception("No entry found")

    def get_data(self, id: int) -> dict[str, int | str]:
        resp = self.table.get(id)

        if resp:
            return {"id": id, **resp}

        raise Exception("No entry found")


def _session() -> Generator[DB, None, None]:
    yield DB()


class Calendar(BaseModel):
    id: int
    date: str
    day: str


@app.get("/", response_model=Calendar)
@app.get("/id/{id}", response_model=Calendar)
@app.get("/year/{year}/{month}", response_model=Calendar)
def get(
    *,
    id: Optional[int] = None,
    year: Optional[int] = None,
    month: Optional[int] = None,
    session: DB = Depends(_session),
) -> dict[str, int | str]:
    if not id and not year and not month:
        today = datetime.date(2023, 12, 5)

        year = today.year
        month = today.month

    if year and month:
        id = session.get_id_by_date(year, month)

    return session.get_data(id)
