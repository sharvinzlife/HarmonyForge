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
export PLEX_BASE_URL="http://192.168.1.100:32400"
export PLEX_TOKEN="replace-with-your-token"
export PLEX_MUSIC_SECTION="6"
```

## 3) Run
```bash
plexh verify-artists --show 10
```

## 4) Full cycle example
```bash
mkdir -p reports

plexh export-artist-tracks \
  --artist-names "Various Artists,V.A.,Verschillende artiesten" \
  --out-csv reports/various_targets.csv

plexh retag-from-csv \
  --in-csv reports/various_targets.csv \
  --out-csv reports/retag_report.csv \
  --path-map "/Music=/mnt/nas/music"

plexh cleanup-artists \
  --artist-names "Various Artists,V.A.,Verschillende artiesten" \
  --scan-csv reports/various_targets.csv \
  --scan-root-prefix "/Music" \
  --path-map "/Music=/Music" \
  --section-refresh

plexh repair-artist-posters \
  --fix-missing --fix-corrupt --generate-missing \
  --path-map "/Music=/mnt/nas/music" \
  --out-csv reports/poster_report.csv
```

## 5) Optional SSH alias pattern
```bash
ssh nas-music
```

Use your own host alias configured in `~/.ssh/config`.
