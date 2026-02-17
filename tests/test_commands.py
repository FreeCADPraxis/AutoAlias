from __future__ import annotations

import unittest

from SketcherAutoAlias.commands.cmd_create_alias_now import CreateAliasNowCommand
from SketcherAutoAlias.commands.cmd_toggle_auto_alias import ToggleAutoAliasCommand


class _FakeController:
    def __init__(self) -> None:
        self.toggle_count = 0
        self.manual_count = 0

    def is_active(self) -> bool:
        return True

    def is_enabled(self) -> bool:
        return True

    def toggle_enabled(self):
        self.toggle_count += 1
        return True

    def run_manual_sync(self):
        self.manual_count += 1
        return 1


class CommandSignatureTests(unittest.TestCase):
    def test_toggle_activated_accepts_optional_checked_arg(self) -> None:
        controller = _FakeController()
        command = ToggleAutoAliasCommand(controller)

        command.Activated()
        command.Activated(True)

        self.assertEqual(controller.toggle_count, 2)

    def test_create_now_activated_accepts_optional_arg(self) -> None:
        controller = _FakeController()
        command = CreateAliasNowCommand(controller)

        command.Activated()
        command.Activated(False)

        self.assertEqual(controller.manual_count, 2)


if __name__ == "__main__":
    unittest.main()

