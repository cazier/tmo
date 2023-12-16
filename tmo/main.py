import pathlib
from typing import Annotated

import typer
import uvicorn

app = typer.Typer()

# pylint: disable=import-outside-toplevel


@app.command()
def serve(
    host: Annotated[str, typer.Option(help="Socket address")] = "0.0.0.0",
    port: Annotated[int, typer.Option(help="Socket port")] = 8000,
    reload: bool = typer.Option(default=False, help="enable auto-reload"),
) -> None:
    uvicorn.run("tmo.db.api:app", host=host, port=port, reload=reload, reload_includes=["*.j2"] if reload else None)


@app.command("import")
def import_from_json(path: Annotated[pathlib.Path, typer.Option(help="path to json file")]) -> None:
    from tmo.db.tools.json_import import run

    run(path)


@app.command()
def playground() -> None:
    import logging

    import IPython
    from sqlmodel import Session, SQLModel, create_engine, func, select  # pylint: disable=unused-import

    from tmo.db.highlight import LOGGER_NAME, SqlHandler

    engine = create_engine("sqlite://", echo=True)

    logging.getLogger(LOGGER_NAME).addHandler(SqlHandler())

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:  # pylint: disable=unused-variable
        IPython.embed(display_banner=False)  # type: ignore[no-untyped-call]


@app.command()
def info() -> None:
    print("Version: v1.0.0")


if __name__ == "__main__":
    app()
