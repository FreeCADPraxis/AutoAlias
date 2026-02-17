from __future__ import annotations

import importlib
import sys
import types
import unittest


class _FakeParamGroup:
    def __init__(self, storage):
        self.storage = storage

    def GetBool(self, key: str, default: bool):  # noqa: N802
        return self.storage.get(key, default)

    def SetBool(self, key: str, value: bool):  # noqa: N802
        self.storage[key] = bool(value)

    def GetString(self, key: str, default: str):  # noqa: N802
        return self.storage.get(key, default)

    def SetString(self, key: str, value: str):  # noqa: N802
        self.storage[key] = str(value)


class InitGuiTests(unittest.TestCase):
    def setUp(self) -> None:
        self._saved_modules = {name: sys.modules.get(name) for name in ("FreeCAD", "FreeCADGui")}
        self._install_fake_freecad_modules()
        self._clear_plugin_modules()

    def tearDown(self) -> None:
        self._clear_plugin_modules()
        for name, module in self._saved_modules.items():
            if module is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = module

    def _clear_plugin_modules(self) -> None:
        for name in list(sys.modules):
            if name.startswith("SketcherAutoAlias") and ".tests" not in name:
                sys.modules.pop(name, None)

    def _install_fake_freecad_modules(self) -> None:
        app = types.ModuleType("FreeCAD")
        gui = types.ModuleType("FreeCADGui")
        self.app = app
        self.gui = gui

        pref_storage = {}

        class _Console:
            def PrintMessage(self, _msg):  # noqa: N802
                return None

            def PrintWarning(self, _msg):  # noqa: N802
                return None

            def PrintError(self, _msg):  # noqa: N802
                return None

        app.Console = _Console()
        app.ActiveDocument = object()
        app._observers = []

        def _param_get(path: str):
            return _FakeParamGroup(pref_storage.setdefault(path, {}))

        def _add_document_observer(observer):
            app._observers.append(observer)

        def _remove_document_observer(observer):
            if observer in app._observers:
                app._observers.remove(observer)

        app.ParamGet = _param_get
        app.addDocumentObserver = _add_document_observer
        app.removeDocumentObserver = _remove_document_observer

        class _ActiveWorkbench:
            def __init__(self) -> None:
                self.reloaded = 0

            def reloadActive(self):  # noqa: N802
                self.reloaded += 1

        class _Selection:
            @staticmethod
            def getSelection():  # noqa: N802
                return []

        gui.Selection = _Selection
        gui._commands = {}
        gui._manipulators = []
        gui._active_workbench = _ActiveWorkbench()

        def _add_command(name, command):
            gui._commands[name] = command

        def _add_workbench_manipulator(manipulator):
            gui._manipulators.append(manipulator)

        def _remove_workbench_manipulator(manipulator):
            if manipulator in gui._manipulators:
                gui._manipulators.remove(manipulator)

        def _active_workbench():
            return gui._active_workbench

        gui.addCommand = _add_command
        gui.addWorkbenchManipulator = _add_workbench_manipulator
        gui.removeWorkbenchManipulator = _remove_workbench_manipulator
        gui.activeWorkbench = _active_workbench

        sys.modules["FreeCAD"] = app
        sys.modules["FreeCADGui"] = gui

    def test_import_installs_commands_observer_and_manipulator(self) -> None:
        importlib.import_module("SketcherAutoAlias.InitGui")

        self.assertIn("SketcherAutoAlias_CreateAliasNow", self.gui._commands)
        self.assertIn("SketcherAutoAlias_Toggle", self.gui._commands)
        self.assertEqual(len(self.gui._manipulators), 1)
        self.assertTrue(hasattr(self.gui, "SPREADSHEET_ALIAS_WB_MANIPULATOR"))
        self.assertGreaterEqual(self.gui._active_workbench.reloaded, 1)
        self.assertEqual(len(self.app._observers), 1)

    def test_manipulator_targets_spreadsheet_toolbar(self) -> None:
        importlib.import_module("SketcherAutoAlias.InitGui")

        manipulator = self.gui.SPREADSHEET_ALIAS_WB_MANIPULATOR
        config = manipulator.modifyToolBars()
        self.assertIn(
            {"append": "SketcherAutoAlias_CreateAliasNow", "toolBar": "Spreadsheet"},
            config,
        )
        self.assertIn(
            {"append": "SketcherAutoAlias_Toggle", "toolBar": "Spreadsheet"},
            config,
        )

    def test_import_survives_controller_import_failure(self) -> None:
        broken_controller = types.ModuleType("SketcherAutoAlias.core.controller")
        saved = sys.modules.get("SketcherAutoAlias.core.controller")
        sys.modules["SketcherAutoAlias.core.controller"] = broken_controller
        sys.modules.pop("SketcherAutoAlias.InitGui", None)

        try:
            importlib.import_module("SketcherAutoAlias.InitGui")
            # No crash during import, and no manipulator because controller setup aborted.
            self.assertEqual(len(self.gui._manipulators), 0)
        finally:
            if saved is None:
                sys.modules.pop("SketcherAutoAlias.core.controller", None)
            else:
                sys.modules["SketcherAutoAlias.core.controller"] = saved


if __name__ == "__main__":
    unittest.main()
