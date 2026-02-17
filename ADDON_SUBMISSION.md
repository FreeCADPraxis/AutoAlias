# FreeCAD Addon Submission

## 1. Fill metadata placeholders
Edit `/Users/andre/Projects/freecad/SketcherAutoAlias/package.xml`:
- Replace `REPLACE_WITH_YOUR_USER` in all GitHub URLs.
- Optionally set maintainer email in `<maintainer email="...">`.
- Update `<version>` and `<date>` for each release.

## 2. Push plugin repository
Publish this folder as a public GitHub repository:
- Repo name should match the addon ID in catalog: `SketcherAutoAlias`.
- Default branch in the catalog entry below is `main`.

## 3. Add catalog entry in FreeCAD-addons
Fork and open a PR against:
- `https://github.com/FreeCAD/FreeCAD-addons`

Add this entry to `AddonCatalog.json`:

```json
"SketcherAutoAlias": [
  {
    "freecad_min": "1.1.0",
    "repository": "https://github.com/REPLACE_WITH_YOUR_USER/SketcherAutoAlias",
    "git_ref": "main"
  }
]
```

## 4. Verify in FreeCAD
After merge and cache refresh:
- Open FreeCAD Addon Manager.
- Click refresh.
- Filter includes package type `Other` or `All`.
- Search `Sketcher Auto Alias`.
