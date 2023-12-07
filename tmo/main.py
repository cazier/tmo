import pathlib
from typing import Annotated

import typer
import uvicorn

app = typer.Typer()


@app.command()
def serve(
    host: Annotated[str, typer.Option(help="Socket address")] = "0.0.0.0",
    port: Annotated[int, typer.Option(help="Socket port")] = 8000,
    reload: bool = typer.Option(default=False, help="enable auto-reload"),
) -> None:
    uvicorn.run("tmo.db.api:app", host=host, port=port, reload=reload, reload_includes=["*.j2", "*.py"])


@app.command("import")
def import_from_json(path: Annotated[pathlib.Path, typer.Option(help="path to json file")]) -> None:
    from tmo.db.tools.json_import import run  # pylint: disable=import-outside-toplevel

    run(path)


@app.command()
def info() -> None:
    print("Version: v1.0.0")


if __name__ == "__main__":
    app()
