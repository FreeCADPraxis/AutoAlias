"""Plugin controller for command wiring and observer lifecycle."""

from __future__ import annotations

from typing import List, Set

from .alias_service import AliasService
from .constants import COMMAND_CREATE_NOW, COMMAND_TOGGLE
from .freecad_api import App, Gui
from .logging_utils import info, warn
from .observers import SpreadsheetObserver
from .prefs import Preferences
from .spreadsheet_utils import get_selected_sheets, is_sheet_object


def _sheet_key(sheet: object) -> str:
    document = getattr(sheet, "Document", None)
    doc_file = getattr(document, "FileName", "")
    if isinstance(doc_file, str) and doc_file.strip():
        doc_name = doc_file.strip()
    else:
        doc_name = getattr(document, "Name", "<NoDocument>")
    obj_name = getattr(sheet, "Name", "<NoName>")
    return f"{doc_name}::{obj_name}"


class SketcherAutoAliasController:
    def __init__(self) -> None:
        self._prefs = Preferences()
        self._alias_service = AliasService(self._prefs)
        self._observer = SpreadsheetObserver(self.handle_sheet_change)
        self._observer_registered = False
        self._commands_registered = False
        self._active_sync: Set[str] = set()

    def command_names(self) -> List[str]:
        return [COMMAND_TOGGLE, COMMAND_CREATE_NOW]

    def register_commands(self) -> None:
        if self._commands_registered or Gui is None:
            return

        from SketcherAutoAlias.commands.cmd_create_alias_now import CreateAliasNowCommand
        from SketcherAutoAlias.commands.cmd_toggle_auto_alias import ToggleAutoAliasCommand

        Gui.addCommand(COMMAND_TOGGLE, ToggleAutoAliasCommand(self))
        Gui.addCommand(COMMAND_CREATE_NOW, CreateAliasNowCommand(self))
        self._commands_registered = True

    def start_observer(self) -> None:
        if App is None or self._observer_registered:
            return
        if not hasattr(App, "addDocumentObserver"):
            return
        App.addDocumentObserver(self._observer)
        self._observer_registered = True

    def stop_observer(self) -> None:
        if App is None or not self._observer_registered:
            return
        if not hasattr(App, "removeDocumentObserver"):
            return
        App.removeDocumentObserver(self._observer)
        self._observer_registered = False

    def is_enabled(self) -> bool:
        return self._prefs.is_auto_alias_enabled()

    def toggle_enabled(self) -> bool:
        new_value = not self.is_enabled()
        self._prefs.set_auto_alias_enabled(new_value)
        state = "enabled" if new_value else "disabled"
        info(f"Automatic spreadsheet alias sync {state}.")
        return new_value

    def is_active(self) -> bool:
        return App is not None and getattr(App, "ActiveDocument", None) is not None

    def run_manual_sync(self) -> int:
        if App is None:
            return 0

        document = getattr(App, "ActiveDocument", None)
        if document is None:
            warn("No active document.")
            return 0

        sheets = get_selected_sheets()
        if not sheets:
            sheets = list(self._alias_service.iter_document_sheets(document))

        if not sheets:
            warn("No spreadsheets found. Create or select a spreadsheet first.")
            return 0

        total = 0
        for sheet in sheets:
            total += self.handle_sheet_change(sheet, "ManualCommand", True)

        if total:
            info(f"Manual sync finished. Updated {total} alias(es).")
        else:
            info("Manual sync finished. Nothing to update.")
        return total

    def handle_sheet_change(self, sheet: object, _prop: str, force: bool) -> int:
        if not is_sheet_object(sheet):
            return 0
        if not force and not self.is_enabled():
            return 0

        key = _sheet_key(sheet)
        if key in self._active_sync:
            return 0

        self._active_sync.add(key)
        try:
            return self._alias_service.sync_sheet(sheet)
        finally:
            self._active_sync.discard(key)


CONTROLLER = SketcherAutoAliasController()

