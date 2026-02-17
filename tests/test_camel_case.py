from __future__ import annotations

import unittest

from SketcherAutoAlias.core.camel_case import to_camel_case, to_valid_alias


class CamelCaseTests(unittest.TestCase):
    def test_to_camel_case_basic(self) -> None:
        self.assertEqual(to_camel_case("wall thickness"), "wallThickness")
        self.assertEqual(to_camel_case("Wall_Thickness"), "wallThickness")
        self.assertEqual(to_camel_case("größe außen"), "groesseAussen")

    def test_to_valid_alias_normalization(self) -> None:
        self.assertEqual(to_valid_alias("123 width"), "v123_width")
        self.assertEqual(to_valid_alias("  "), "var")
        self.assertEqual(to_valid_alias("höhe"), "hoehe")
        self.assertEqual(to_valid_alias("wand höhe"), "wand_hoehe")
        self.assertEqual(to_valid_alias("Blech-Deckel"), "blech_deckel")


if __name__ == "__main__":
    unittest.main()
