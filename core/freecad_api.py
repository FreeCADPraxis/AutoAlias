"""Helpers for importing FreeCAD modules safely."""

from __future__ import annotations

try:
    import FreeCAD as App  # type: ignore
except Exception:  # pragma: no cover - only happens outside FreeCAD
    App = None

try:
    import FreeCADGui as Gui  # type: ignore
except Exception:  # pragma: no cover - only happens in console/no-gui runs
    Gui = None


def has_app() -> bool:
    return App is not None


def has_gui() -> bool:
    return Gui is not None

