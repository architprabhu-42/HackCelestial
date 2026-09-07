$ErrorActionPreference = 'Stop'
param(
  [string]$BaseUrl = 'http://127.0.0.1:8000',
  [string]$TripId = 'trip:mumbai-goa-v2'
)

$snapshot = Invoke-RestMethod -Method Get -Uri "$BaseUrl/api/v1/trips/$TripId"
$body = @{ expected_trip_version = $snapshot.snapshot.trip.version; scenario_id = 'mumbai-goa-v2' } | ConvertTo-Json
$result = Invoke-RestMethod -Method Post -Uri "$BaseUrl/api/v1/trips/$TripId/reset" -ContentType 'application/json' -Body $body
Write-Host "Reset applied: version $($result.current_trip_version)."
