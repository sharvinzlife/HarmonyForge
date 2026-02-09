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

## Run
```powershell
plexh verify-artists --server plex --show 10
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
plexh retag-from-csv `
  --server plex `
  --in-csv reports\targets.csv `
  --out-csv reports\retag_report.csv `
  --path-map "/Music=Z:\\Music"
```

## Track numbering fix example
```powershell
plexh fix-track-numbers `
  --server plex `
  --in-csv reports\targets.csv `
  --out-csv reports\tracknumber_report.csv `
  --path-map "/Music=Z:\\Music" `
  --preserve-total
```
