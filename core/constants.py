"""Constants used by the SketcherAutoAlias plugin."""

from __future__ import annotations

import os

PARAM_PATH = "User parameter:BaseApp/Preferences/Mod/SketcherAutoAlias"

PREF_AUTO_ALIAS_ENABLED = "AutoAliasEnabled"

DEFAULT_AUTO_ALIAS_ENABLED = True

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICON_DIR = os.path.join(ROOT_DIR, "resources", "icons")
ICON_TOGGLE = os.path.join(ICON_DIR, "toggle_auto_alias.svg")
ICON_CREATE = os.path.join(ICON_DIR, "create_alias_now.svg")

COMMAND_TOGGLE = "SketcherAutoAlias_Toggle"
COMMAND_CREATE_NOW = "SketcherAutoAlias_CreateAliasNow"
