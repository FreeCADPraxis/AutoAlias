"""Preferences storage for SketcherAutoAlias."""

from __future__ import annotations

from .constants import (
    DEFAULT_AUTO_ALIAS_ENABLED,
    PARAM_PATH,
    PREF_AUTO_ALIAS_ENABLED,
)
from .freecad_api import App


class Preferences:
    def __init__(self) -> None:
        self._group = App.ParamGet(PARAM_PATH) if App is not None else None

    def get_bool(self, key: str, default: bool) -> bool:
        if self._group is None:
            return default
        try:
            return bool(self._group.GetBool(key, default))
        except Exception:
            return default

    def set_bool(self, key: str, value: bool) -> None:
        if self._group is None:
            return
        self._group.SetBool(key, bool(value))

    def is_auto_alias_enabled(self) -> bool:
        return self.get_bool(PREF_AUTO_ALIAS_ENABLED, DEFAULT_AUTO_ALIAS_ENABLED)

    def set_auto_alias_enabled(self, enabled: bool) -> None:
        self.set_bool(PREF_AUTO_ALIAS_ENABLED, enabled)
