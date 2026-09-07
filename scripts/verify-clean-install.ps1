param([string]$Destination = (Join-Path (Split-Path -Parent $PSScriptRoot) 'artifacts\clean-install-verify'))

$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
if (Test-Path $Destination) { throw "Destination already exists: $Destination. Choose an empty temporary directory." }
New-Item -ItemType Directory -Force $Destination | Out-Null
foreach ($name in @('apps', 'contracts', 'data', 'docs', 'scripts', '.tools')) {
  $source = Join-Path $root $name
  $target = Join-Path $Destination $name
  $excluded = if ($name -eq '.tools') { @() } else { @('node_modules', '.venv', 'dist', 'local', '.pytest_cache', '.pytest-tmp', '.uv-cache', 'test-results', 'playwright-report', '.contract-check-tmp') }
  $arguments = @($source, $target, '/E', '/NFL', '/NDL', '/NJH', '/NJS', '/NP')
  if ($excluded.Count) { $arguments += @('/XD') + $excluded }
  & robocopy @arguments
  if ($LASTEXITCODE -gt 7) { throw "robocopy failed for $name with exit code $LASTEXITCODE" }
}
Copy-Item -LiteralPath (Join-Path $root 'README.md') -Destination (Join-Path $Destination 'README.md')

Push-Location $Destination
try {
  & '.\scripts\bootstrap.ps1'
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
  & '.\scripts\test-all.ps1'
  if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
} finally { Pop-Location }
