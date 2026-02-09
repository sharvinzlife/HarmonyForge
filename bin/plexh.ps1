$ErrorActionPreference = "Stop"
$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
if ($env:PYTHONPATH) {
  $env:PYTHONPATH = "$($Root.Path)\src;$($env:PYTHONPATH)"
} else {
  $env:PYTHONPATH = "$($Root.Path)\src"
}
python -m plex_music_hygiene.cli @args
