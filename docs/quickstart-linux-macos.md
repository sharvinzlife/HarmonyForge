# Linux and macOS Quickstart

## Get the repo
```bash
git clone https://github.com/sharvinzlife/HarmonyForge.git
cd HarmonyForge
```

## 🐧 Linux Install (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## 🍎 macOS Install
```bash
brew install python
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Configure
```bash
export MEDIA_SERVER="plex"
export PLEX_BASE_URL="http://192.168.1.100:32400"
export PLEX_TOKEN="replace-with-your-token"
export PLEX_MUSIC_SECTION="6"
```

### Token note
- Token is not hardcoded in HarmonyForge.
- Get it from Plex Web -> item `...` -> `Get Info` -> `View XML` -> copy `X-Plex-Token`.

## Run
```bash
plexh verify-artists --server plex --show 10
```

## Run doctor first
```bash
plexh doctor --server plex \
  --path-map "/Music=/mnt/nas/music" \
  --scan-root-prefix "/Music"
```

## Full cycle example (simple)
```bash
mkdir -p reports
```

### Path note
- `/Music` in commands = Plex library root path.
- `/mnt/nas/music` = your shell-visible NAS mount path.
- Change both values if your environment is different.

### 1) Export problematic tracks
```bash
plexh export-artist-tracks \
  --server plex \
  --artist-names "Various Artists,V.A.,Verschillende artiesten" \
  --out-csv reports/various_targets.csv
```

### 2) Fix album and albumartist tags
```bash
plexh retag-from-csv \
  --server plex \
  --in-csv reports/various_targets.csv \
  --out-csv reports/retag_report.csv \
  --path-map "/Music=/mnt/nas/music"
```

### 3) Fix tracknumber tags from filenames
```bash
plexh fix-track-numbers \
  --server plex \
  --in-csv reports/various_targets.csv \
  --out-csv reports/tracknumber_report.csv \
  --path-map "/Music=/mnt/nas/music" \
  --preserve-total
```

### 4) Remove stale artist buckets and rescan
```bash
plexh cleanup-artists \
  --server plex \
  --artist-names "Various Artists,V.A.,Verschillende artiesten" \
  --scan-csv reports/various_targets.csv \
  --scan-root-prefix "/Music" \
  --path-map "/Music=/Music" \
  --section-refresh
```

### 5) Repair missing/corrupt posters
```bash
plexh repair-artist-posters \
  --server plex \
  --fix-missing --fix-corrupt --generate-missing \
  --path-map "/Music=/mnt/nas/music" \
  --out-csv reports/poster_report.csv
```

## Optional SSH alias pattern
```bash
ssh nas-music
```

Use your own host alias configured in `~/.ssh/config`.
