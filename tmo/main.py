import pathlib
from typing import Annotated, Optional

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
    uvicorn.run(
        "tmo.web:app",
        host=host,
        port=port,
        reload=reload,
        reload_includes=["*.j2", "*.js", "config.toml"] if reload else None,
    )


@app.command("import")
def import_from_json(path: Annotated[pathlib.Path, typer.Option(help="path to json file")]) -> None:
    from tmo.db.tools.json_import import run

    run(path)


@app.command()
def playground(db: Annotated[Optional[pathlib.Path], typer.Option(help="Path to a sqlite database")] = None) -> None:
    # pylint: disable=unused-import,unused-variable,too-many-locals
    from unittest.mock import patch

    import IPython
    from sqlmodel import Session, func, select

    from tmo.config import database
    from tmo.db.highlight import db_print
    from tmo.db.models import Bill, Charge, Detail, Subscriber

    updates: dict[str, str | bool]

    if db is not None:
        updates = {"path": str(db.resolve().relative_to(pathlib.Path.cwd()))}

    else:
        updates = {"memory": True}

    with patch.dict(database, {"dialect": "sqlite", "echo": True, **updates}, clear=True):
        from tmo.db.engines import engine

    with Session(engine) as session:
        IPython.embed(display_banner=False)  # type: ignore[no-untyped-call]


@app.command()
def info() -> None:
    import rich

    from tmo import __version__

    rich.print("[bold underline2 blue]T-Mobile Bills[/]")
    rich.print(f" [green]v{__version__.MAJOR}.{__version__.MINOR}.{__version__.PATCH}")


if __name__ == "__main__":
    app()
