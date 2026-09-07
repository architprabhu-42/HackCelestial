# ResiliTrip

ResiliTrip is a local-first travel-disruption recovery demonstration. It uses the fictional Mumbai → Goa scenario only: every schedule, fare and option is **synthetic and not bookable**. It never makes provider bookings, cancellations or payments.

## Windows PowerShell quick start

Prerequisites: Windows PowerShell 5.1+ (or PowerShell 7), Node 22, Python 3.12, `uv` and npm. Docker Desktop is optional. `bootstrap` installs only from `apps/api/uv.lock` and `apps/web/package-lock.json`.

```powershell
./scripts/bootstrap.ps1
./scripts/test-all.ps1
```

Start the built local application:

```powershell
Push-Location apps/web; npm run build; Pop-Location
Push-Location apps/api
..\..\.venv\Scripts\python.exe -m uvicorn resilitrip.main:app --host 127.0.0.1 --port 8000
Pop-Location
```

Open `http://127.0.0.1:8000`. Use **Reset scenario** in the app to return a demo trip to baseline. See [docs/DEMO_RUNBOOK.md](docs/DEMO_RUNBOOK.md) for the presenter script and troubleshooting.

## Verification commands

```powershell
./scripts/test-unit.ps1
./scripts/test-contract.ps1
./scripts/test-golden.ps1
./scripts/test-integration.ps1
./scripts/test-e2e.ps1
./scripts/test-offline.ps1
./scripts/test-performance.ps1
./scripts/test-all.ps1
./scripts/verify-clean-install.ps1
```

`test-all` is fail-fast and never rewrites accepted goldens, screenshots, OpenAPI/types or lockfiles. The performance command writes only `artifacts/performance/hero-benchmark.json`.
