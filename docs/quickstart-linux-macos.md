# Linux and macOS Quickstart

## 1) Install
```bash
cd plex-music-hygiene
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## 2) Configure
```bash
export PLEX_BASE_URL="http://10.1.0.105:32400"
export PLEX_TOKEN="your-token"
export PLEX_MUSIC_SECTION="6"
```

## 3) Run
```bash
plexh verify-artists --show 10
```

## 4) Full cycle example
```bash
plexh export-artist-tracks \
  --artist-names "Various Artists,V.A.,Verschillende artiesten" \
  --out-csv reports/various_targets.csv

plexh retag-from-csv \
  --in-csv reports/various_targets.csv \
  --out-csv reports/retag_report.csv \
  --path-map "/LHarmony-Music=/mnt/remotes/LHARMONY-NAS_data/media/music"

plexh cleanup-artists \
  --artist-names "Various Artists,V.A.,Verschillende artiesten" \
  --scan-csv reports/various_targets.csv \
  --path-map "/LHarmony-Music=/LHarmony-Music" \
  --section-refresh

plexh repair-artist-posters \
  --fix-missing --fix-corrupt --generate-missing \
  --path-map "/LHarmony-Music=/mnt/remotes/LHARMONY-NAS_data/media/music" \
  --out-csv reports/poster_report.csv
```
