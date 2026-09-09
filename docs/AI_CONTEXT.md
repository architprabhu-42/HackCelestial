# ResiliTrip AI Context

## Start here

ResiliTrip is a local-first, single-container travel-disruption recovery demo. The only supported scenario is a fictional Mumbai-to-Goa trip. All inventory, schedules, fares, and policies are synthetic and never create bookings, cancellations, refunds, or payments.

Before changing code, inspect `graphify-out/GRAPH_REPORT.md` for a broad map or query `graphify-out/graph.json` with Graphify. Read the relevant normative document in `docs/` before changing domain behavior, fixture values, API contracts, or user-facing claims.

## Architecture

- `apps/api`: FastAPI REST API, application orchestration, pure domain engine, and SQLite persistence. Domain code must not import FastAPI, SQLAlchemy, or frontend/map libraries.
- `apps/web`: React, TypeScript, and Vite presentation layer. It displays versioned backend snapshots and must not independently certify feasibility, time, money, ranking, or plan identity.
- `data/fixtures/mumbai-goa-v2.json`: canonical deterministic hero fixture.
- `contracts/openapi.json`: exported API contract; generated web API types must stay synchronized with it.
- `docs/01_*` through `docs/09_*`: product, domain, fixture, algorithm, architecture, API, UX, and test specifications. Document 01 wins if they conflict.

## Core invariants

- Feasibility precedes ranking. A plan must satisfy every hard constraint.
- Recovery starts from the traveler’s actual time, location, and boarding state; never teleport a traveler to a more convenient origin.
- Use the shared backend constraint evaluator for impact, planning, and plan adoption. Unknown required facts are not feasible.
- Keep cash required now separate from unreceived refunds and already-paid costs.
- Alternatives are assembled from atomic services and transfers; recommendation cards are not hardcoded.
- A selected plan is an internal proposed itinerary only. The UI must retain the synthetic/not-bookable disclosure and never claim a provider action.
- Preserve snapshot versions and stale-state protection on all mutations.
- The offline core—including fixture, planner, graph/table, local geometry, and reset—must work without external APIs or map tiles.

## Local workflow

```powershell
./scripts/bootstrap.ps1
./scripts/test-all.ps1
```

Run targeted checks with `test-unit.ps1`, `test-contract.ps1`, `test-golden.ps1`, `test-integration.ps1`, `test-e2e.ps1`, `test-offline.ps1`, or `test-performance.ps1`. `test-all.ps1` is fail-fast and must not rewrite accepted goldens, snapshots, generated OpenAPI/types, or lockfiles.

To run the built application, build `apps/web` and start the API from `apps/api` with the repository `.venv` as described in `README.md`. The app serves the web bundle and API from the same origin.

## Change safety

- Changes to frozen Mumbai-Goa acceptance values require corresponding fixture, expected-result, and test updates.
- Do not introduce provider calls, payment/booking behavior, live-map dependencies, remote planning models, microservices, additional Uvicorn workers, or duplicate client-side domain logic without an approved design change.
- Keep API, generated types, fixtures, golden outputs, and tests synchronized.
- After code changes, refresh the graph with `graphify update .`; document or image changes require a full Graphify refresh to retain semantic coverage.

## Graph MCP

Graphify exposes `query_graph`, `get_node`, `get_neighbors`, `get_community`, `god_nodes`, `graph_stats`, and `shortest_path` through a local stdio MCP server. Configure it with the Graphify tool interpreter and the absolute path to `graphify-out/graph.json`; this machine-specific registration is intentionally not committed.
