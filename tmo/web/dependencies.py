import typing

from fastapi import Depends
from sqlmodel import Session

from ..db.engines import start_engine

engine = None


def get_session() -> typing.Generator[Session, None, None]:
    global engine

    if engine is None:
        engine = start_engine()

    with Session(engine) as session:
        yield session


SessionDependency = typing.Annotated[Session, Depends(get_session)]
