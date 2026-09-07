$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$python = Join-Path $root ".tools\python"
$node = Join-Path $root ".tools\node-v22.17.1-win-x64\node.exe"
$generator = Join-Path $root "apps\web\node_modules\openapi-typescript\bin\cli.js"
$temporary = Join-Path $root ".contract-check-tmp"

$env:Path = "$python;$(Join-Path $root '.tools\uv');$env:Path"
New-Item -ItemType Directory -Force $temporary | Out-Null
Push-Location (Join-Path $root 'apps\api')
try {
  uv run --locked --group dev pytest -p no:cacheprovider tests/contract
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} finally { Pop-Location }
uv run --locked --project (Join-Path $root "apps\api") python -m resilitrip.tools.export_openapi --output (Join-Path $temporary "openapi.json")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
& $node $generator (Join-Path $temporary "openapi.json") --output (Join-Path $temporary "schema.d.ts")
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
if ((Get-Content -Raw (Join-Path $temporary "openapi.json")) -cne (Get-Content -Raw (Join-Path $root "contracts\openapi.json"))) { throw "Committed OpenAPI differs; regenerate contracts/openapi.json." }
if ((Get-Content -Raw (Join-Path $temporary "schema.d.ts")) -cne (Get-Content -Raw (Join-Path $root "apps\web\src\api\schema.d.ts"))) { throw "Committed TypeScript differs; regenerate apps/web/src/api/schema.d.ts." }
