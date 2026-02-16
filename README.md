# SketcherAutoAlias

FreeCAD plugin for spreadsheet aliases.

## Behavior
- No Sketcher actions are used.
- The plugin reads name texts from any spreadsheet cell.
- For each supported source cell, it creates/updates an alias on the right neighbor cell.

Example:
- `A1 = wall thickness`
- `B1 = 5 mm`
- Result: alias `wall_thickness` points to `B1`.

Also works in other columns:
- `D4 = wand höhe`
- `E4 = 2400 mm`
- Result: alias `wand_hoehe` points to `E4`.

## Commands
- `Auto Alias (On/Off)`:
1. Enables/disables automatic alias refresh when a Spreadsheet changes.
- `Create Alias Now`:
1. Runs sync immediately for selected spreadsheets.
2. If nothing is selected, runs sync for all spreadsheets in the active document.

## Install
1. Copy `SketcherAutoAlias` into your FreeCAD `Mod` directory.
2. Restart FreeCAD.
3. Open the normal `Spreadsheet` workbench.
4. Use toolbar buttons:
`Create Alias Now` and `Auto Alias (On/Off)`.

Typical user mod paths:
- Linux: `~/.local/share/FreeCAD/Mod`
- macOS: `~/Library/Application Support/FreeCAD/Mod`
- Windows: `%APPDATA%\\FreeCAD\\Mod`

## Preferences
Saved under:
`User parameter:BaseApp/Preferences/Mod/SketcherAutoAlias`

Keys:
- `AutoAliasEnabled` (bool, default `true`)

## Notes
- Separators are normalized:
`space -> _`, `- -> _`.
- Alias collisions are handled with numeric suffixes:
`name`, `name2`, `name3`, ...
- If the right-neighbor target cell is empty, it is initialized to `0` before assigning alias.
# AutoAlias
