import pathlib

from fastapi import staticfiles

from .pages import router

static = staticfiles.StaticFiles(directory=pathlib.Path(__file__).parent.joinpath("static"))

__all__ = ["router", "static"]
