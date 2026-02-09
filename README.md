# HarmonyForge (plex-music-hygiene)

Portable Plex music repair toolkit for:
- fixing bad artist buckets (`Various Artists`, `V.A.`, localized variants)
- repairing `album` and `albumartist` tags in bulk
- repairing missing/corrupt artist posters
- exporting CSV audit trails for every operation

![HarmonyForge logo](assets/logo.svg)

## Why this persists
Tag and folder fixes are written to media files and filesystem paths, so they survive Plex appdata loss and full rescans.

## Install
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Windows PowerShell:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

## Configure
```bash
export PLEX_BASE_URL="http://10.1.0.105:32400"
export PLEX_TOKEN="your-token"
export PLEX_MUSIC_SECTION="6"
```

## One command interface
After install:
```bash
plexh --help
```

Without install:
- Linux/macOS: `./bin/plexh verify-artists --show 10`
- Windows: `.\bin\plexh.ps1 verify-artists --show 10`

## Typical workflow
```bash
mkdir -p reports

plexh export-artist-tracks \
  --artist-names "Various Artists,V.A.,Verschillende artiesten" \
  --out-csv reports/targets.csv

plexh retag-from-csv \
  --in-csv reports/targets.csv \
  --out-csv reports/retag_report.csv \
  --path-map "/LHarmony-Music=/mnt/remotes/LHARMONY-NAS_data/media/music"

plexh cleanup-artists \
  --artist-names "Various Artists,V.A.,Verschillende artiesten" \
  --scan-csv reports/targets.csv \
  --path-map "/LHarmony-Music=/LHarmony-Music" \
  --section-refresh

plexh repair-artist-posters \
  --fix-missing --fix-corrupt --generate-missing \
  --path-map "/LHarmony-Music=/mnt/remotes/LHARMONY-NAS_data/media/music" \
  --out-csv reports/poster_report.csv

plexh verify-artists --show 20
```

## Architecture
See `docs/architecture.md` (Mermaid diagrams included).

## Docs
- Linux/macOS quickstart: `docs/quickstart-linux-macos.md`
- Windows quickstart: `docs/quickstart-windows.md`
- Publish to GitHub: `docs/github-publish.md`
- Name ideas: `docs/name-ideas.md`

## Safety notes
- Start with `retag-from-csv --dry-run` if needed.
- Avoid `--empty-trash` unless you intentionally want Plex DB cleanup and know media delete is disabled in Plex settings.
