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

## Run
```bash
plexh verify-artists --server plex --show 10
```

## Full cycle example
```bash
mkdir -p reports

plexh export-artist-tracks \
  --server plex \
  --artist-names "Various Artists,V.A.,Verschillende artiesten" \
  --out-csv reports/various_targets.csv

plexh retag-from-csv \
  --server plex \
  --in-csv reports/various_targets.csv \
  --out-csv reports/retag_report.csv \
  --path-map "/Music=/mnt/nas/music"

plexh cleanup-artists \
  --server plex \
  --artist-names "Various Artists,V.A.,Verschillende artiesten" \
  --scan-csv reports/various_targets.csv \
  --scan-root-prefix "/Music" \
  --path-map "/Music=/Music" \
  --section-refresh

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
