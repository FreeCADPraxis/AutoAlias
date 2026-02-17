"""FreeCAD GUI entry point for SketcherAutoAlias."""

from __future__ import annotations


def _run_init() -> None:
    try:
        import FreeCADGui as Gui  # type: ignore
    except Exception:
        return

    def local_warn(message: str) -> None:
        try:
            import FreeCAD as App  # type: ignore

            if hasattr(App, "Console"):
                App.Console.PrintWarning(f"[SketcherAutoAlias] {message}\n")
        except Exception:
            pass

    # Register commands and observer.
    try:
        from SketcherAutoAlias.core.controller import CONTROLLER

        CONTROLLER.register_commands()
        CONTROLLER.start_observer()
    except Exception as exc:
        local_warn(f"Controller could not be loaded: {exc}")
        return

    # Inject commands into the existing Spreadsheet workbench toolbar.
    try:
        if not hasattr(Gui, "addWorkbenchManipulator"):
            local_warn("WorkbenchManipulator API is not available in this FreeCAD build.")
            return

        class LocalSpreadsheetAliasWBManipulator:
            def modifyToolBars(self):
                return [
                    {"append": "SketcherAutoAlias_CreateAliasNow", "toolBar": "Spreadsheet"},
                    {"append": "SketcherAutoAlias_Toggle", "toolBar": "Spreadsheet"},
                ]

        existing = getattr(Gui, "SPREADSHEET_ALIAS_WB_MANIPULATOR", None)
        if existing is not None and hasattr(Gui, "removeWorkbenchManipulator"):
            try:
                Gui.removeWorkbenchManipulator(existing)
            except Exception:
                pass

        manipulator = LocalSpreadsheetAliasWBManipulator()
        Gui.SPREADSHEET_ALIAS_WB_MANIPULATOR = manipulator
        Gui.addWorkbenchManipulator(manipulator)

        if hasattr(Gui, "activeWorkbench"):
            try:
                active = Gui.activeWorkbench()
                if active and hasattr(active, "reloadActive"):
                    active.reloadActive()
            except Exception:
                pass
    except Exception as exc:
        local_warn(f"Failed to install Spreadsheet toolbar integration: {exc}")


_run_init()

