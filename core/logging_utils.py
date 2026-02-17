"""Small logging wrapper for FreeCAD console messages."""

from __future__ import annotations

from .freecad_api import App

PREFIX = "[SketcherAutoAlias] "


def _print(level: str, message: str) -> None:
    if App is None or not hasattr(App, "Console"):
        return
    line = PREFIX + message.rstrip() + "\n"
    if level == "warn":
        App.Console.PrintWarning(line)
    elif level == "err":
        App.Console.PrintError(line)
    else:
        App.Console.PrintMessage(line)


def info(message: str) -> None:
    _print("info", message)


def warn(message: str) -> None:
    _print("warn", message)


def error(message: str) -> None:
    _print("err", message)

