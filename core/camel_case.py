"""Alias normalization and camelCase conversion."""

from __future__ import annotations

import re
import unicodedata

WORD_RE = re.compile(r"[A-Za-z0-9]+")
SEPARATOR_RE = re.compile(r"[\s-]+")
IDENT_RE = re.compile(r"[^A-Za-z0-9_]")
UNDERSCORE_RE = re.compile(r"_+")
UMLAUT_MAP = str.maketrans(
    {
        "ä": "ae",
        "ö": "oe",
        "ü": "ue",
        "Ä": "Ae",
        "Ö": "Oe",
        "Ü": "Ue",
        "ß": "ss",
    }
)


def _normalize_text(raw: str) -> str:
    text = (raw or "").strip()
    if not text:
        return ""
    text = text.translate(UMLAUT_MAP)
    # Drop other accents/diacritics but keep ASCII base chars.
    text = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in text if not unicodedata.combining(ch))


def to_camel_case(raw: str) -> str:
    text = _normalize_text(raw)
    if not text:
        return "var"

    words = WORD_RE.findall(text)
    if not words:
        return "var"

    head = words[0].lower()
    tail = "".join(part[:1].upper() + part[1:].lower() for part in words[1:])
    return head + tail


def to_valid_alias(raw: str) -> str:
    text = _normalize_text(raw)
    if not text:
        return "var"

    text = SEPARATOR_RE.sub("_", text)
    alias = text.lower()
    alias = IDENT_RE.sub("", alias)
    alias = UNDERSCORE_RE.sub("_", alias).strip("_")
    if not alias:
        alias = "var"
    if alias[0].isdigit():
        alias = "v" + alias
    return alias
