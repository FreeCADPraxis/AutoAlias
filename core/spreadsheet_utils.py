"""Spreadsheet helper functions."""

from __future__ import annotations

from typing import Iterable, List

from .freecad_api import Gui


def is_sheet_object(obj: object) -> bool:
    type_id = getattr(obj, "TypeId", "")
    return isinstance(type_id, str) and type_id.startswith("Spreadsheet::Sheet")


def iter_document_sheets(doc: object) -> Iterable[object]:
    for obj in getattr(doc, "Objects", []):
        if is_sheet_object(obj):
            yield obj


def get_selected_sheets() -> List[object]:
    if Gui is None:
        return []
    try:
        selected = Gui.Selection.getSelection()
    except Exception:
        return []
    return [obj for obj in selected if is_sheet_object(obj)]

