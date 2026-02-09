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
$env:PLEX_BASE_URL = "http://10.1.0.105:32400"
$env:PLEX_TOKEN = "your-token"
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
