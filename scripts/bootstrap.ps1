$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$toolsDir = Join-Path $repoRoot '.tools'
$env:Path = "$(Join-Path $toolsDir 'uv');$(Join-Path $toolsDir 'node-v22.17.1-win-x64');$env:Path"
$env:UV_CACHE_DIR = Join-Path $repoRoot '.uv-cache'
$env:UV_PYTHON_INSTALL_DIR = Join-Path $toolsDir 'python'

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) { throw 'uv is required.' }
if (-not (Get-Command node -ErrorAction SilentlyContinue)) { throw 'Node 22 is required.' }
if (-not ((node --version) -like 'v22.*')) { throw 'Node 22 is required.' }

$pythonExe = uv python find 3.12
if ($LASTEXITCODE -ne 0) { throw 'Install CPython 3.12 with uv before running bootstrap.' }
uv sync --project (Join-Path $repoRoot 'apps/api') --locked --group dev --python $pythonExe
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
Push-Location (Join-Path $repoRoot 'apps/web')
try {
  npm ci
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
  npx playwright install chromium
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
finally { Pop-Location }
