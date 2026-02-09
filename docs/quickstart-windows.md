# Windows Quickstart

## 1) Install
```powershell
cd plex-music-hygiene
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

## 2) Configure
```powershell
$env:PLEX_BASE_URL = "http://192.168.1.100:32400"
$env:PLEX_TOKEN = "replace-with-your-token"
$env:PLEX_MUSIC_SECTION = "6"
```

## 3) Run
```powershell
plexh verify-artists --show 10
```

## Optional wrapper without install
```powershell
.\bin\plexh.ps1 verify-artists --show 10
```

## Path mapping example
```powershell
plexh retag-from-csv `
  --in-csv reports\targets.csv `
  --out-csv reports\retag_report.csv `
  --path-map "/Music=Z:\\Music"
```
