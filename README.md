# 🎵 HarmonyForge

<p align="center">
  <img src="Harmony-Forge-Logo.png" alt="HarmonyForge logo" width="780" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Plex-Supported-E5A00D?logo=plex&logoColor=black" alt="Plex" />
  <img src="https://img.shields.io/badge/Jellyfin-Supported_for_file_tag_workflows-00A4DC" alt="Jellyfin" />
  <img src="https://img.shields.io/badge/Emby-Supported_for_file_tag_workflows-52B54B" alt="Emby" />
  <img src="https://img.shields.io/badge/CI-Linux%20%7C%20macOS%20%7C%20Windows-2088FF?logo=githubactions&logoColor=white" alt="CI" />
  <img src="https://img.shields.io/badge/Docs-Mermaid-FF4081" alt="Mermaid" />
</p>

<p align="center">
  <strong>🧹 Clean metadata • 🖼️ repair artist covers • 📄 keep audit trails</strong>
</p>

## 🚀 Multi-Purpose Scope
HarmonyForge is built as a media-library hygiene toolkit for **Plex, Jellyfin, and Emby**, with practical workflows for cleanup and long-term organization.

### ✨ Why It Is Useful
1. It removes messy artist buckets like `Various Artists`, `V.A.`, and language variants.
2. It standardizes tags so libraries regroup correctly after scans.
3. It repairs missing/corrupt artist posters.
4. It keeps CSV audit reports so changes are traceable and repeatable.
5. It helps maintain clean albums with correct track numbering tags.

### 🧰 Feature Map
1. **API-driven cleanup (Plex today)**
: `export-artist-tracks`, `cleanup-artists`, `repair-artist-posters`, `verify-artists`
2. **Server-agnostic file-tag hygiene**
: `retag-from-csv` updates `album` and `albumartist` based on target folders
3. **Track numbering correction**
: `fix-track-numbers` reads leading numbers from filenames (for example `01 - Song.flac`) and writes `tracknumber`
4. **Cross-platform execution**
: Linux/macOS/Windows wrappers and CI matrix
5. **Portable project structure**
: reusable scripts, docs, diagrams, and report outputs

### 🔧 Backend Support Status
1. ✅ **Plex API workflows**: implemented
2. ✅ **Jellyfin/Emby file-tag workflows**: implemented (file operations are server-agnostic)
3. 🛠️ **Jellyfin/Emby API adapters**: planned

Use `--server plex|jellyfin|emby` to select backend behavior.

## 🧭 Architecture (Mermaid)
```mermaid
flowchart LR
  U[User / Admin] --> C[plexh CLI]
  C --> M[Metadata Tag Engine]
  C --> N[Track Number Normalizer]
  C --> A[Server Adapter]
  M --> F[Music Files on NAS]
  N --> F
  A --> P[Plex API]
  A --> J[Jellyfin API Adapter Planned]
  A --> E[Emby API Adapter Planned]
  C --> R[CSV Reports]
```

## 🌐 Generic Environment Setup
```bash
export MEDIA_SERVER="plex"
export PLEX_BASE_URL="http://192.168.1.100:32400"
export PLEX_TOKEN="replace-with-your-token"
export PLEX_MUSIC_SECTION="6"
```

PowerShell:
```powershell
$env:MEDIA_SERVER = "plex"
$env:PLEX_BASE_URL = "http://192.168.1.100:32400"
$env:PLEX_TOKEN = "replace-with-your-token"
$env:PLEX_MUSIC_SECTION = "6"
```

## ⚡ Super Quick Start
```bash
git clone https://github.com/sharvinzlife/HarmonyForge.git
cd HarmonyForge
```

## ⚙️ Install By Platform

### 🐧 Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 🍎 macOS
```bash
brew install python
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 🪟 Windows (PowerShell)
```powershell
winget install -e --id Python.Python.3.11
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

### 💻 Windows (CMD)
```cmd
python -m venv .venv
.venv\Scripts\activate.bat
pip install -e .
```

## 🛠️ One Command Interface
After install:
```bash
plexh --help
```

Without install:
- Linux/macOS: `./bin/plexh verify-artists --show 10`
- Windows PowerShell: `.\bin\plexh.ps1 verify-artists --show 10`
- Windows CMD: `bin\plexh.cmd verify-artists --show 10`

## 📚 Typical Workflow
```bash
mkdir -p reports

plexh export-artist-tracks \
  --server plex \
  --artist-names "Various Artists,V.A.,Verschillende artiesten" \
  --out-csv reports/targets.csv

plexh retag-from-csv \
  --server plex \
  --in-csv reports/targets.csv \
  --out-csv reports/retag_report.csv \
  --path-map "/Music=/mnt/nas/music"

plexh fix-track-numbers \
  --server plex \
  --in-csv reports/targets.csv \
  --out-csv reports/tracknumber_report.csv \
  --path-map "/Music=/mnt/nas/music" \
  --preserve-total

plexh cleanup-artists \
  --server plex \
  --artist-names "Various Artists,V.A.,Verschillende artiesten" \
  --scan-csv reports/targets.csv \
  --scan-root-prefix "/Music" \
  --path-map "/Music=/Music" \
  --section-refresh

plexh repair-artist-posters \
  --server plex \
  --fix-missing --fix-corrupt --generate-missing \
  --path-map "/Music=/mnt/nas/music" \
  --out-csv reports/poster_report.csv

plexh verify-artists --server plex --show 20
```

## 🧪 Tests
```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

## 🗂️ Docs
- `docs/architecture.md`
- `docs/quickstart-linux-macos.md`
- `docs/quickstart-windows.md`
- `docs/github-publish.md`
- `docs/name-ideas.md`

## ✅ Persistence Notes
- File tag and folder fixes persist across media server rebuilds.
- Server DB-only poster assignments may need rerun after DB reset.

## ⚠️ Safety
- Start with `retag-from-csv --dry-run` for new libraries.
- Avoid `--empty-trash` unless media deletion is disabled.
