"""Command: run manual alias generation."""

from __future__ import annotations

from SketcherAutoAlias.core.constants import ICON_CREATE


class CreateAliasNowCommand:
    def __init__(self, controller) -> None:
        self._controller = controller

    def GetResources(self) -> dict:  # noqa: N802 (FreeCAD API)
        return {
            "Pixmap": ICON_CREATE,
            "MenuText": "Create Alias Now",
            "ToolTip": "Create/update spreadsheet aliases from name cells into the right neighbor value cells.",
        }

    def IsActive(self) -> bool:  # noqa: N802
        return self._controller.is_active()

    def Activated(self, *args) -> None:  # noqa: N802
        self._controller.run_manual_sync()
