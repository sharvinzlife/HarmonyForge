# plex-music-hygiene
Reusable toolkit for Plex music cleanup and recovery:
- export tracks under bad artist buckets (for example `Various Artists`)
- retag files from Plex-exported CSV (`album` and `albumartist`)
- repair missing/corrupt artist posters
- delete stale artist metadata and trigger rescans
- verify poster integrity across the full artist library

## Requirements
- Python 3.8+
- `mutagen` (`pip install mutagen`)
- optional: `Pillow` for generated fallback covers (`pip install pillow`)
- Plex token with access to the target server

## Quick Start
```bash
export PLEX_BASE_URL="http://127.0.0.1:32400"
export PLEX_TOKEN="<your-token>"
export PLEX_MUSIC_SECTION="6"
```

Verify state:
```bash
python3 scripts/plex_music_toolkit.py verify-artists
```

Export tracks currently grouped under bad artists:
```bash
python3 scripts/plex_music_toolkit.py export-artist-tracks \
  --artist-names "Various Artists,Verschillende artiesten" \
  --out-csv various_artist_tracks.csv
```

Retag files from CSV (map Plex mount path to host filesystem path):
```bash
python3 scripts/plex_music_toolkit.py retag-from-csv \
  --in-csv various_artist_tracks.csv \
  --out-csv retag_report.csv \
  --path-map "/LHarmony-Music=/mnt/remotes/LHARMONY-NAS_data/media/music"
```

Cleanup stale artist entries and trigger targeted rescans:
```bash
python3 scripts/plex_music_toolkit.py cleanup-artists \
  --artist-names "Various Artists,Verschillende artiesten" \
  --scan-csv various_artist_tracks.csv \
  --path-map "/LHarmony-Music=/LHarmony-Music" \
  --section-refresh \
  --empty-trash \
  --wait-seconds 20
```

Repair artist posters:
```bash
python3 scripts/plex_music_toolkit.py repair-artist-posters \
  --out-csv poster_repair_report.csv \
  --fix-missing \
  --fix-corrupt \
  --generate-missing \
  --path-map "/LHarmony-Music=/mnt/remotes/LHARMONY-NAS_data/media/music"
```

## Persistence Notes
- File tag edits (`album`, `albumartist`) are persistent in media files and survive Plex appdata loss.
- Plex DB-only artwork assignments do not survive appdata loss unless equivalent local cover files exist.
- Keep this toolkit and rerun when rebuilding Plex metadata.

## Safety
- Start with `retag-from-csv --dry-run`.
- Keep CSV reports for audit trails.
- Use targeted scan CSV for controlled rescans.
