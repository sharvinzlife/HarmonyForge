# HarmonyForge Design (2026-02-09)

## Goal
Create a reusable, auditable Plex music operations toolkit that works on Linux, macOS, and Windows with one command surface.

## Approaches considered
1. Keep one monolithic script only.
Tradeoff: quickest, but weak packaging and poor cross-platform ergonomics.

2. Convert to installable Python package plus wrappers.
Tradeoff: slightly more setup now, much better portability and maintainability.

3. Full multi-service architecture with DB and web UI.
Tradeoff: overkill for current scope and slower iteration.

Recommended: approach 2.

## Architecture
- Core module: `src/plex_music_hygiene/cli.py`
- Thin compatibility wrapper: `scripts/plex_music_toolkit.py`
- Cross-platform launchers: `bin/plexh`, `bin/plexh.ps1`, `bin/plexh.cmd`
- Reports-first workflow with CSV outputs for auditability
- Plex API integration for targeted scan and metadata cleanup
- mutagen integration for deterministic file tag editing

## Data flow
1. Export target tracks from problematic artist buckets.
2. Retag files based on expected folder mapping.
3. Remove stale artist records and refresh paths.
4. Repair poster metadata from album art or local files.
5. Verify final artist/poster state.

## Error handling
- Preserve per-file/per-artist status in CSV reports.
- Continue processing on failures.
- Surface operation totals in stdout.

## Testing and verification
- Syntax check with `python3 -m py_compile`.
- CLI smoke check with `python3 -m plex_music_hygiene.cli --help`.
- Report validation by line counts and known status distribution.
