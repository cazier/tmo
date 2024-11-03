import typing
from sqlmodel import Session

from fastapi import Depends


from tmo.db.engines import engine

def get_session() -> typing.Generator[Session, None, None]:
    with Session(engine) as session:
        yield session

SessionDependency = typing.Annotated[Session, Depends(get_session)]