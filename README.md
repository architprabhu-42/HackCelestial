# ResiliTrip

ResiliTrip currently is a local-first travel-disruption recovery demonstration. It
uses the fictional Mumbai → Goa scenario only: every schedule, fare and option is
**synthetic and not bookable**. It never makes provider bookings, cancellations or
payments.

## Documentation

- [Current demo architecture](docs/CURRENT_DEMO_ARCHITECTURE.md) and
  [AI onboarding context](docs/AI_CONTEXT.md)
- [Future implementation roadmap](docs/IMPLEMENTATION_PLAN.md) — planned work, not
  currently shipped
- [Product decisions](docs/01_Product_Decision_and_Scope_Lock.md),
  [requirements](docs/02_Product_Requirements_Document.md),
  [target architecture](docs/06_Technical_Architecture_Specification.md), and
  [target UX](docs/08_UX_Interaction_and_Demo_Specification.md)
- [Demo runbook](docs/DEMO_RUNBOOK.md) and the retained current-demo references:
  [domain](docs/03_Domain_Model_and_India_Travel_Glossary.md),
  [fixture](docs/04_Reference_Scenario_and_Fixture_Specification.md),
  [algorithms](docs/05_Algorithm_and_Recovery_Planning_Specification.md),
  [API contract](docs/07_API_and_Data_Contract_Specification.md), and
  [tests](docs/09_Test_Strategy_and_Golden_Validation_Specification.md).

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
