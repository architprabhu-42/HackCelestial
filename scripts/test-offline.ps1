$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $PSScriptRoot
$env:Path = "$(Join-Path $repoRoot '.tools\node-v22.17.1-win-x64');$env:Path"
Push-Location (Join-Path $repoRoot 'apps/web')
try {
  npm run build
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
  npx playwright test e2e/offline.spec.ts --project=chromium --reporter=list
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} finally { Pop-Location }
