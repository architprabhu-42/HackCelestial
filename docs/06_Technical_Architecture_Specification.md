# ResiliTrip — Technical Architecture

**Document:** 06 of the ResiliTrip implementation set
**Status:** target architecture for roadmap work; it describes intended changes, not features already present.
**Authority:** `IMPLEMENTATION_PLAN.md` sets delivery order; Documents 01 and 02 set product decisions and requirements.

## Architectural shape

Keep a modular local application:

```text
React/TypeScript UI → same-origin /api/v1 → FastAPI application layer
                                          → pure domain/evaluator/search
                                          → provider adapters and SQLite repositories
```

The frontend renders server snapshots and owns presentation state only. The domain layer owns validation, continuity, feasibility, ranking and plan identity and must not import FastAPI, browser, map or database code. Provider adapters normalize external responses into evidence-bearing records before domain evaluation.

## Core boundaries

| Boundary | Rule |
| --- | --- |
| UI | No duplicate feasibility/ranking/money engine. Keep response-version checks and discard stale responses. |
| API | Keep `/api/v1`, error envelope, version checks and demo reset. Evolve OpenAPI and generated TypeScript with each slice. |
| Application | Coordinates reads, evidence fetches, jobs and transactions; performs no hidden domain-rule forks. |
| Domain | Models real/demo, draft/active, transport graph, physical route, dependency DAG, alternatives, evidence, money and evaluation. |
| Providers | Fetch outside write transactions; report coverage/failure explicitly; no fabricated fallback facts. |
| Persistence | SQLite stores migrations, immutable versions, evidence, jobs, selected plans and exportable local state. |
| Demo | Uses isolated fixture/catalog/clock/data namespace and remains operable offline. |

## Data and migration design

Add schema migrations before generic-trip writes. Every migration needs forward and rollback/compatibility tests. Preserve legacy demo snapshot hashes and history through a reader plus explicit conversion; never reinterpret demo data as real.

Persist versions for trips, drafts, events, evidence, alternatives, jobs and selections. Store money as paise plus exact/range/unknown semantics and scope. Store evidence source, observed time, expiry/retention policy and coverage state. Completed history is immutable; edits create a new version and stale mutations fail with the standard version conflict response.

## Planning and jobs

Provider calls happen before pure evaluation. A planning request creates a persisted job, returns its identifier, and is later read, cancelled or resumed after restart. The worker must cap search time, expansions and provider quota; partial results name the bound reached. The evaluator is the shared authority for impact, candidate testing and adoption. Search uses stable state IDs/revisions and retains its past/onboard prefix rather than teleporting a traveler.

## API evolution

Add slices rather than a parallel API: trip list/create/read; draft save/update and non-mutating validation; place/service search; transfer estimation; source capability lookup; disruption/constraint updates; planning job create/read/cancel; preview and acknowledged adoption; evidence retrieval; local export/import.

Each slice updates Pydantic DTOs, OpenAPI, generated frontend types, examples, runtime guards and contract tests together. Preserve existing demo endpoints and error semantics until a versioned replacement is implemented.

## Operational and security rules

- Keep one local deployment boundary unless a later approved decision changes it.
- Measure local-core and provider latency separately; record bounded provider failures and job outcomes without leaking restricted data.
- Enforce provider attribution and retention in UI, storage, logs and exports.
- Keep service secrets server-side. Restrict browser keys to the smallest approved map surface, and provide a complete list/SVG fallback.
- The current synthetic demo’s offline behavior is a regression requirement.

## Implementation checkpoints

Foundation establishes test/migration/source records. R1 implements generic domain and persistence; R2 trip creation; R3 provider adapters/search/jobs; R4 UI/map fallback; R5 transaction, export and retention safety; R6 release proof. Each checkpoint requires behavior, contract and migration evidence before proceeding.
