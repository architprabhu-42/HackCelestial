$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$env:Path = "$(Join-Path $repoRoot '.tools/uv');$env:Path"
$env:UV_CACHE_DIR = Join-Path $repoRoot '.uv-cache'
New-Item -ItemType Directory -Force (Join-Path $repoRoot '.pytest-tmp') | Out-Null
Push-Location (Join-Path $repoRoot 'apps/api')
try {
  uv run --locked --group dev pytest -p no:cacheprovider --basetemp "$repoRoot/.pytest-tmp/golden" tests/unit/test_fixture_and_baseline.py::test_t03_baseline_snapshot_matches_document_04
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
finally { Pop-Location }
