# Architecture

## High Level
```mermaid
flowchart LR
  U[Operator] --> C[plexh CLI]
  C --> T[Tag Engine (mutagen)]
  C --> N[Track Number Normalizer]
  C --> A[Server Adapter]
  T --> F[Music Files]
  N --> F
  A --> P[Plex API (Implemented)]
  A --> J[Jellyfin API (Planned)]
  A --> E[Emby API (Planned)]
  C --> R[Reports CSV]
```

## Cleanup Pipeline
```mermaid
flowchart TD
  A[Export bad artist tracks] --> B[Retag album and albumartist]
  B --> C[Fix track numbering from filenames]
  C --> D[Refresh targeted server paths]
  D --> E[Delete stale artist shells]
  E --> F[Verify artist search hits]
  F --> G[Repair missing and corrupt artist posters]
  G --> H[Final verification and reports]
```

## Script Layout
```mermaid
graph TD
  CLI[src/plex_music_hygiene/cli.py]
  W1[scripts/plex_music_toolkit.py]
  W2[bin/plexh]
  W3[bin/plexh.ps1]
  W4[bin/plexh.cmd]
  CLI --> API[PlexClient]
  CLI --> TAG[mutagen tag editor]
  CLI --> POSTER[poster repair]
  W1 --> CLI
  W2 --> CLI
  W3 --> CLI
  W4 --> CLI
```
