# Windows Quickstart

## Get the repo
```powershell
git clone https://github.com/sharvinzlife/HarmonyForge.git
cd HarmonyForge
```

## 🪟 Install (PowerShell)
```powershell
winget install -e --id Python.Python.3.11
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

## 💻 Install (CMD)
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
pip install -e .
```

## Configure
```powershell
$env:MEDIA_SERVER = "plex"
$env:PLEX_BASE_URL = "http://192.168.1.100:32400"
$env:PLEX_TOKEN = "replace-with-your-token"
$env:PLEX_MUSIC_SECTION = "6"
```

### Token note
- Token is not hardcoded in HarmonyForge.
- Get it from Plex Web -> item `...` -> `Get Info` -> `View XML` -> copy `X-Plex-Token`.

## Run
```powershell
plexh verify-artists --server plex --show 10
```

## Interactive setup wizard
```powershell
plexh
```

## Run doctor first
```powershell
plexh doctor --server plex `
  --path-map "/Music=Z:\\Music" `
  --scan-root-prefix "/Music"
```

## Optional wrappers without install
```powershell
.\bin\plexh.ps1 verify-artists --server plex --show 10
```

```cmd
bin\plexh.cmd verify-artists --server plex --show 10
```

## Path mapping example
```powershell
# `/Music` = Plex library root path
# `Z:\Music` = your mapped NAS path in Windows
# 1) Export problematic tracks
plexh export-artist-tracks `
  --server plex `
  --artist-names "Various Artists,V.A.,Verschillende artiesten" `
  --out-csv reports\targets.csv

# 2) Fix album + albumartist tags
plexh retag-from-csv `
  --server plex `
  --in-csv reports\targets.csv `
  --out-csv reports\retag_report.csv `
  --path-map "/Music=Z:\\Music"
```

## Track numbering fix example
```powershell
# 3) Fix tracknumber tags from filenames
plexh fix-track-numbers `
  --server plex `
  --in-csv reports\targets.csv `
  --out-csv reports\tracknumber_report.csv `
  --path-map "/Music=Z:\\Music" `
  --preserve-total

# 4) Remove stale artist buckets and rescan
plexh cleanup-artists `
  --server plex `
  --artist-names "Various Artists,V.A.,Verschillende artiesten" `
  --scan-csv reports\targets.csv `
  --scan-root-prefix "/Music" `
  --path-map "/Music=/Music" `
  --section-refresh

# 5) Repair missing/corrupt artist posters
plexh repair-artist-posters `
  --server plex `
  --fix-missing --fix-corrupt --generate-missing `
  --path-map "/Music=Z:\\Music" `
  --out-csv reports\poster_report.csv
```
