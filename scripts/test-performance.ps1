$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$env:Path = "$(Join-Path $repoRoot '.tools\uv');$env:Path"
$env:UV_CACHE_DIR = Join-Path $repoRoot '.uv-cache'
Push-Location (Join-Path $repoRoot 'apps/api')
try {
  uv run --locked --group dev python -m resilitrip.tools.hero_benchmark
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} finally { Pop-Location }
