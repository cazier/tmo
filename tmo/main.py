import pathlib
from typing import Annotated, Optional

import typer
import uvicorn

app = typer.Typer()


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
            "tmo.web:app",
            host=host,
            port=port,
            reload=reload,
            reload_includes=["*.j2", "*.js", "config.toml"] if reload else None,
            reload_excludes=["./tests/*"] if reload else None,
            env_file=root,
        )


@app.command("import")
def import_from_json(
    path: Annotated[pathlib.Path, typer.Option(help="path to json file")],
    config_file: Annotated[Optional[pathlib.Path], typer.Option("--config", help="Path to a config file")] = None,
) -> None:
    from tmo import Config
    from tmo.db.tools.json_import import run

    if config_file:
        Config.from_file(config_file)

    run(path)


@app.command()
def playground(
    config_file: Annotated[Optional[pathlib.Path], typer.Option("--config", help="Path to a config file")] = None,
    db: Annotated[Optional[pathlib.Path], typer.Option(help="Path to a sqlite database")] = None,
    show_sql: Annotated[bool, typer.Option(help="Show SQL statements")] = False,
) -> None:
    # ruff: noqa: F401, F841
    import IPython
    from sqlmodel import Session, func, select

    from tmo import config
    from tmo.db.highlight import db_print
    from tmo.db.models import Bill, Charge, Detail, Subscriber

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
        from tmo.db.engines import start_engine

        engine = start_engine()

        with Session(engine) as session:
            IPython.embed(display_banner=False)  # type: ignore[no-untyped-call]


@app.command()
def info() -> None:
    from tmo import __version__

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
