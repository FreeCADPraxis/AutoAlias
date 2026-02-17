"""Document observer callbacks for spreadsheet changes."""

from __future__ import annotations

from typing import Callable

from .spreadsheet_utils import is_sheet_object


class SpreadsheetObserver:
    def __init__(self, on_change: Callable[[object, str, bool], None]) -> None:
        self._on_change = on_change

    def slotChangedObject(self, *args) -> None:  # noqa: N802 (FreeCAD naming)
        if len(args) < 2:
            return
        obj, prop = args[0], str(args[1])
        if not is_sheet_object(obj):
            return
        if prop.startswith("View"):
            return
        self._on_change(obj, prop, False)

    def slotCreatedObject(self, *args) -> None:  # noqa: N802
        if not args:
            return
        obj = args[0]
        if not is_sheet_object(obj):
            return
        self._on_change(obj, "CreatedObject", True)

