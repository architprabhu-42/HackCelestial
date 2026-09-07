$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$env:Path = "$(Join-Path $repoRoot '.tools/uv');$env:Path"
$env:UV_CACHE_DIR = Join-Path $repoRoot '.uv-cache'
New-Item -ItemType Directory -Force (Join-Path $repoRoot '.pytest-tmp') | Out-Null
Push-Location apps/api
try {
  uv run --locked --group dev pytest -p no:cacheprovider --basetemp "$repoRoot/.pytest-tmp/integration" tests/integration
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} finally { Pop-Location }
