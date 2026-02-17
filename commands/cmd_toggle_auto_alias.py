"""Command: enable/disable automatic alias generation."""

from __future__ import annotations

from SketcherAutoAlias.core.constants import ICON_TOGGLE


class ToggleAutoAliasCommand:
    def __init__(self, controller) -> None:
        self._controller = controller

    def GetResources(self) -> dict:  # noqa: N802 (FreeCAD API)
        return {
            "Pixmap": ICON_TOGGLE,
            "MenuText": "Auto Alias (On/Off)",
            "ToolTip": "Enable or disable automatic spreadsheet alias generation.",
            "Checkable": True,
        }

    def IsActive(self) -> bool:  # noqa: N802
        return self._controller.is_active()

    def IsChecked(self) -> bool:  # noqa: N802
        return self._controller.is_enabled()

    def Activated(self, *args) -> None:  # noqa: N802
        self._controller.toggle_enabled()
