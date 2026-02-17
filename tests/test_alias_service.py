from __future__ import annotations

import re
import unittest

from SketcherAutoAlias.core.alias_service import AliasService


class _FakeSheet:
    TypeId = "Spreadsheet::Sheet"

    def __init__(self) -> None:
        self.Name = "Variables"
        self.Label = "Variables"
        self.cells = {}
        self.alias_to_cell = {}

    def isValidAlias(self, alias: str) -> bool:  # noqa: N802
        return bool(re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", alias))

    def getAddressFromAlias(self, alias: str):  # noqa: N802
        return self.alias_to_cell.get(alias, "")

    def getAlias(self, cell: str):  # noqa: N802
        for alias, mapped in self.alias_to_cell.items():
            if mapped == cell:
                return alias
        return ""

    def setAlias(self, cell: str, alias: str) -> None:  # noqa: N802
        for old_alias, old_cell in list(self.alias_to_cell.items()):
            if old_cell == cell and old_alias != alias:
                del self.alias_to_cell[old_alias]
        existing = self.alias_to_cell.get(alias)
        if existing and existing != cell:
            raise ValueError(f"Alias '{alias}' already used in {existing}")
        self.alias_to_cell[alias] = cell

    def get(self, cell: str):
        return self.cells.get(cell, "")

    def set(self, cell: str, value: str) -> None:
        self.cells[cell] = value

    def getNonEmptyCells(self):  # noqa: N802
        return [cell for cell, value in self.cells.items() if str(value).strip()]


class _FakePrefs:
    pass


class AliasServiceTests(unittest.TestCase):
    def test_sync_creates_aliases_from_col_a_to_col_b(self) -> None:
        sheet = _FakeSheet()
        sheet.set("A1", "wall thickness")
        sheet.set("B1", "5 mm")

        service = AliasService(_FakePrefs())
        updated = service.sync_sheet(sheet)

        self.assertEqual(updated, 1)
        self.assertEqual(sheet.alias_to_cell["wall_thickness"], "B1")
        self.assertEqual(sheet.cells["B1"], "5 mm")
        self.assertNotIn("v5_mm", sheet.alias_to_cell)

    def test_sync_handles_duplicate_names_with_suffix(self) -> None:
        sheet = _FakeSheet()
        sheet.set("A1", "wall thickness")
        sheet.set("B1", "5 mm")
        sheet.set("A2", "wall thickness")
        sheet.set("B2", "8 mm")

        service = AliasService(_FakePrefs())
        updated = service.sync_sheet(sheet)

        self.assertEqual(updated, 2)
        self.assertEqual(sheet.alias_to_cell["wall_thickness"], "B1")
        self.assertEqual(sheet.alias_to_cell["wall_thickness2"], "B2")

    def test_sync_initializes_empty_target_cell(self) -> None:
        sheet = _FakeSheet()
        sheet.set("A3", "height")

        service = AliasService(_FakePrefs())
        updated = service.sync_sheet(sheet)

        self.assertEqual(updated, 1)
        self.assertEqual(sheet.cells["B3"], "0")
        self.assertEqual(sheet.alias_to_cell["height"], "B3")

    def test_sync_works_in_any_column(self) -> None:
        sheet = _FakeSheet()
        sheet.set("D4", "wand höhe")
        sheet.set("E4", "2400 mm")

        service = AliasService(_FakePrefs())
        updated = service.sync_sheet(sheet)

        self.assertEqual(updated, 1)
        self.assertEqual(sheet.alias_to_cell["wand_hoehe"], "E4")
        self.assertEqual(sheet.cells["E4"], "2400 mm")


if __name__ == "__main__":
    unittest.main()
