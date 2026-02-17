"""Spreadsheet alias synchronization logic."""

from __future__ import annotations

import re
from typing import Iterable, List, Optional, Tuple

from .camel_case import to_valid_alias
from .logging_utils import info, warn
from .prefs import Preferences

CELL_RE = re.compile(r"^([A-Z]+)([1-9][0-9]*)$")
MAX_COLUMN_INDEX = 16384  # XFD


class AliasService:
    def __init__(self, prefs: Preferences) -> None:
        self._prefs = prefs

    def sync_document(self, document: object) -> int:
        total = 0
        for sheet in self.iter_document_sheets(document):
            total += self.sync_sheet(sheet)
        return total

    def sync_sheet(self, sheet: object) -> int:
        if not self._is_sheet_object(sheet):
            return 0

        source_cells = self._source_cells(sheet)
        if not source_cells:
            return 0

        updates = 0
        label = getattr(sheet, "Label", getattr(sheet, "Name", "Spreadsheet"))

        for name_cell in source_cells:
            raw_name = self._cell_text(sheet, name_cell)
            target_cell = self._cell_to_right(name_cell)
            if not raw_name or not target_cell:
                continue

            base_alias = to_valid_alias(raw_name)
            chosen_alias = self._choose_alias(sheet, base_alias, target_cell)
            if not chosen_alias:
                warn(f"Skipping {name_cell}: alias for '{raw_name}' could not be generated.")
                continue

            if self._cell_is_empty(sheet, target_cell):
                # Keep target cell usable as a value cell if it was untouched.
                self._set_cell(sheet, target_cell, "0")

            if self._alias_points_to(sheet, chosen_alias, target_cell):
                continue

            if self._set_alias(sheet, target_cell, chosen_alias):
                updates += 1
            else:
                warn(f"Failed to set alias '{chosen_alias}' at {target_cell}.")

        if updates:
            info(f"Synced {updates} alias(es) in spreadsheet '{label}'.")
        return updates

    def iter_document_sheets(self, document: object) -> Iterable[object]:
        for obj in getattr(document, "Objects", []):
            if self._is_sheet_object(obj):
                yield obj

    def _source_cells(self, sheet: object) -> List[str]:
        parsed: List[Tuple[int, int, str]] = []
        for cell in self._iter_non_empty_cells(sheet):
            parsed_cell = self._parse_cell(cell)
            if parsed_cell is None:
                continue
            col_index, row_index = parsed_cell
            text = self._cell_text(sheet, cell)
            if not self._looks_like_name_cell(text):
                continue
            if self._cell_has_alias(sheet, cell):
                # Do not treat existing value/alias cells as source labels.
                continue
            if col_index >= MAX_COLUMN_INDEX:
                continue
            parsed.append((row_index, col_index, cell))
        parsed.sort()
        return [cell for _row, _col, cell in parsed]

    def _iter_non_empty_cells(self, sheet: object) -> Iterable[str]:
        if hasattr(sheet, "getNonEmptyCells"):
            try:
                for address in sheet.getNonEmptyCells():
                    text = self._normalize_cell_address(address)
                    if text:
                        yield text
                return
            except Exception:
                pass

        # Fallback if getNonEmptyCells is unavailable.
        max_rows = 2000
        max_cols = 26
        for row in range(1, max_rows + 1):
            for col in range(1, max_cols + 1):
                cell = f"{self._col_index_to_name(col)}{row}"
                if self._cell_text(sheet, cell):
                    yield cell

    def _looks_like_name_cell(self, text: str) -> bool:
        cleaned = (text or "").strip()
        if not cleaned:
            return False
        if cleaned.startswith("="):
            return False
        if cleaned[0].isdigit():
            return False
        if not any(ch.isalpha() for ch in cleaned):
            return False
        return True

    def _cell_to_right(self, cell: str) -> Optional[str]:
        parsed = self._parse_cell(cell)
        if parsed is None:
            return None
        col_index, row_index = parsed
        right_col = col_index + 1
        if right_col > MAX_COLUMN_INDEX:
            return None
        return f"{self._col_index_to_name(right_col)}{row_index}"

    def _parse_cell(self, cell: str) -> Optional[Tuple[int, int]]:
        match = CELL_RE.match((cell or "").upper())
        if not match:
            return None
        col_name, row = match.groups()
        return self._col_name_to_index(col_name), int(row)

    def _col_name_to_index(self, name: str) -> int:
        total = 0
        for char in name:
            total = total * 26 + (ord(char) - ord("A") + 1)
        return total

    def _choose_alias(self, sheet: object, base_alias: str, target_cell: str) -> str:
        alias = base_alias
        suffix = 2

        while suffix < 1000:
            if self._can_use_alias(sheet, alias, target_cell):
                return alias
            alias = f"{base_alias}{suffix}"
            suffix += 1
        return ""

    def _can_use_alias(self, sheet: object, alias: str, target_cell: str) -> bool:
        if not self._is_valid_alias(sheet, alias):
            return False
        occupied = self._get_alias_cell(sheet, alias)
        if not occupied:
            return True
        return occupied.upper() == target_cell.upper()

    def _is_valid_alias(self, sheet: object, alias: str) -> bool:
        if hasattr(sheet, "isValidAlias"):
            try:
                return bool(sheet.isValidAlias(alias))
            except Exception:
                return False
        return bool(re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", alias))

    def _alias_points_to(self, sheet: object, alias: str, target_cell: str) -> bool:
        occupied = self._get_alias_cell(sheet, alias)
        return bool(occupied) and occupied.upper() == target_cell.upper()

    def _get_alias_cell(self, sheet: object, alias: str) -> str:
        if not hasattr(sheet, "getAddressFromAlias"):
            return ""
        try:
            address = sheet.getAddressFromAlias(alias)
        except Exception:
            return ""
        return self._normalize_cell_address(address)

    def _normalize_cell_address(self, address: object) -> str:
        if address is None:
            return ""
        if isinstance(address, str):
            return address.strip().upper()
        if hasattr(address, "toString"):
            try:
                text = str(address.toString() or "").strip().upper()
                if text:
                    return text
            except Exception:
                pass
        if hasattr(address, "column") and hasattr(address, "row"):
            try:
                col = self._col_index_to_name(int(address.column) + 1)
                row = int(address.row) + 1
                return f"{col}{row}"
            except Exception:
                pass
        return str(address).strip().upper()

    def _set_alias(self, sheet: object, cell: str, alias: str) -> bool:
        if not hasattr(sheet, "setAlias"):
            return False
        try:
            sheet.setAlias(cell, alias)
            return True
        except Exception:
            return False

    def _cell_is_empty(self, sheet: object, cell: str) -> bool:
        value = self._get_cell(sheet, cell)
        if value is None:
            return True
        if isinstance(value, str):
            return value.strip() == ""
        return False

    def _cell_text(self, sheet: object, cell: str) -> str:
        value = self._get_cell(sheet, cell)
        if value is None:
            return ""
        return str(value).strip()

    def _get_cell(self, sheet: object, cell: str):
        if not hasattr(sheet, "get"):
            return None
        try:
            return sheet.get(cell)
        except Exception:
            return None

    def _set_cell(self, sheet: object, cell: str, value: str) -> None:
        if not hasattr(sheet, "set"):
            return
        try:
            sheet.set(cell, str(value))
        except Exception as exc:
            warn(f"Unable to set cell {cell}: {exc}")

    def _cell_has_alias(self, sheet: object, cell: str) -> bool:
        if not hasattr(sheet, "getAlias"):
            return False
        try:
            value = sheet.getAlias(cell)
        except Exception:
            return False
        if value is None:
            return False
        return bool(str(value).strip())

    def _is_sheet_object(self, obj: object) -> bool:
        type_id = getattr(obj, "TypeId", "")
        return isinstance(type_id, str) and type_id.startswith("Spreadsheet::Sheet")

    def _col_index_to_name(self, one_based: int) -> str:
        chars = []
        value = one_based
        while value > 0:
            value, rem = divmod(value - 1, 26)
            chars.append(chr(ord("A") + rem))
        return "".join(reversed(chars)) or "A"
