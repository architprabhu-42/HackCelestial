# Current demo architecture

This is a concise reference for the application that exists today. It is not the
future architecture; see [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) for that.

- The app is a local, single-container synthetic Mumbai–Goa disruption-recovery
  demonstration. It performs no booking, cancellation, refund or payment action.
- `apps/api` provides FastAPI routes, application orchestration, a pure domain
  engine and SQLite persistence. Domain code must not depend on HTTP or frontend
  libraries.
- `apps/web` is React, TypeScript and Vite. It renders versioned server snapshots;
  it must not independently certify feasibility, ranking, money or plan identity.
- The demo fixture is `data/fixtures/mumbai-goa-v2.json`; the API contract is
  `contracts/openapi.json`. Generated frontend types must remain synchronized.
- Preserve snapshot versions and stale-state checks. Keep feasibility before ranking,
  traveler continuity, explicit unknown facts, cash-now/refund separation, atomic
  service/transfer alternatives, and the synthetic/not-bookable disclosure.
- The offline core (fixture, planner, graph/table, local geometry and reset) must
  continue to work without external APIs or map tiles.

The old technical-architecture document was deliberately removed after these
currently applicable boundaries were retained here. Future implementation choices
are governed by the roadmap and must be made with source-feasibility evidence.
