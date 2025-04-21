import logging
import pathlib
from typing import Annotated, Optional

import arrow
import typer
import uvicorn

app = typer.Typer()
update = typer.Typer()
app.add_typer(update, name="update")


@app.command()
def serve(
    host: Annotated[str, typer.Option(help="Socket address")] = "0.0.0.0",
    port: Annotated[int, typer.Option(help="Socket port")] = 8000,
    reload: bool = typer.Option(default=False, help="enable auto-reload"),
    config_path: Annotated[pathlib.Path, typer.Option("--config", help="Config path")] = pathlib.Path("config.toml"),
) -> None:
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        root = pathlib.Path(tmpdir).joinpath(".env")
        root.write_text(f"TMO_UVICORN_CONFIG_PATH={config_path}", encoding="utf8")

        uvicorn.run(
            "tmo.web.app:app",
            host=host,
            port=port,
            reload=reload,
            reload_includes=["*.j2", "*.js", "config.toml"] if reload else None,
            reload_excludes=["./tests/*"] if reload else None,
            env_file=root,
        )


@app.command()
def playground(
    config_file: Annotated[Optional[pathlib.Path], typer.Option("--config", help="Path to a config file")] = None,
    db: Annotated[Optional[pathlib.Path], typer.Option(help="Path to a sqlite database")] = None,
    show_sql: Annotated[bool, typer.Option(help="Show SQL statements")] = False,
) -> None:
    # ruff: noqa: F401, F841
    import IPython
    from sqlmodel import Session, func, select

    from . import config
    from .db.highlight import db_print
    from .db.models import Bill, Charge, Detail, Subscriber

    updates: dict[str, str | bool]

    if config_file:
        config.from_file(config_file)
        updates = {}

    else:
        if db is not None and db != pathlib.Path("memory"):
            updates = {"path": str(db.resolve().relative_to(pathlib.Path.cwd()))}

        else:
            updates = {"dialect": "memory"}

        updates["echo"] = show_sql

    with config.patch(database=updates):
        from .db.engines import start_engine

        engine = start_engine()

        with Session(engine) as session:
            IPython.embed(display_banner=False)  # type: ignore[no-untyped-call]


@update.command(help="Update the database with a single month's data fetched as a CSV")
def fetch(
    date: Annotated[Optional[str], typer.Option(help="Bill date (Format YYYY-MM-DD). Must exist on webpage")] = None,
    verbose: Annotated[bool, typer.Option(help="Sets logging level to DEBUG")] = False,
    headed: Annotated[bool, typer.Option(help="Use a headed browser")] = False,
    config_file: Annotated[Optional[pathlib.Path], typer.Option("--config", help="Path to a config file")] = None,
) -> None:
    import asyncio
    import os

    from . import config
    from .loaders.bulk import api
    from .loaders.fetch import Fetcher, format_csv

    if config_file:
        config.from_file(config_file)

    if not config.fetch:
        typer.echo("Cannot fetch without an entry in the config file", err=True)
        raise typer.Exit(1)

    for key in ("username", "password", "totp_secret"):
        os.environ[f"TMO_FETCH_{key}"] = getattr(config.fetch, key)

    if verbose:
        logging.getLogger("tmo.loaders.fetch").setLevel(logging.DEBUG)

    if date:
        _date = arrow.get(date)

    else:
        _date = arrow.now()

    fetcher = Fetcher(headless=not headed)
    csv = asyncio.run(fetcher.get_csv(date=_date))

    data = format_csv(csv)

    if not api(data=data):
        raise typer.Exit(1)


@update.command("bulk", help="Update the database in bulk with a JSON file")
def bulk(
    path: Annotated[pathlib.Path, typer.Option(help="path to json file")],
    config_file: Annotated[Optional[pathlib.Path], typer.Option("--config", help="path to a config file")] = None,
) -> None:
    from . import config
    from .loaders.bulk import write_db

    if config_file:
        config.from_file(config_file)

    write_db(path)


@app.command()
def info() -> None:
    from . import __version__

    head = "T-Mobile Bills"
    version = f" v{__version__.MAJOR}.{__version__.MINOR}.{__version__.PATCH}"

    try:
        from rich import print

        head = f"[bold underline2 blue]{head}[/]"
        version = f"[green]{version}[/]"

    except ImportError:
        pass

    print(head)
    print(version)


if __name__ == "__main__":
    app()
