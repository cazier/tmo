import pathlib

from fastapi import staticfiles

static = staticfiles.StaticFiles(directory=pathlib.Path(__file__).parent.joinpath("static"))

__all__ = ["static"]
