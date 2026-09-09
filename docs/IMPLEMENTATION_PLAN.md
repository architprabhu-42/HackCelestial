# ResiliTrip implementation roadmap

**Status:** adopted roadmap; planned work only.  
**Source:** `ResiliTrip_Full_Proposed_Solution.md`, supplied outside this repository and intentionally left unchanged.  
**Authority:** this roadmap decides future product direction. The retained numbered
specifications document the current synthetic demo baseline; they do not restrict
the roadmap where they conflict.

## Target and boundaries

ResiliTrip will become a local-first application for creating, checking, saving,
reopening, disrupting, recovering and selecting an itinerary for an unfamiliar
trip. It must work honestly when travel facts are unavailable or uncertain. The
fictional Mumbai–Goa journey remains as a separate, explicitly synthetic,
non-bookable demonstration mode.

Keep the React/TypeScript frontend, FastAPI/Python backend and SQLite. Build with
free sources only and without a delivery-date assumption. A feature is not complete
until a non-demo trip can follow this flow:

```text
create → validate → save/reopen → report disruption → recover → preview/select → reopen
```

No payments, bookings, provider cancellations, PNR/refund handling, live ML,
weather/chat features, public hosting, or self-hosted national transport inventory
are in scope. Provider data remains a feasibility gate, never a promise.

## Delivery sequence

### Foundation — establish a safe baseline

- Treat this roadmap as the forward-looking authority; keep the retained
  specifications as current-demo references.
- Capture a clean test baseline, architecture decisions, source capability records,
  and migration/rollback policy before feature work.
- Keep the demo data and history identifiable as demo data forever; a later generic
  model must not silently relabel it as real.
- Record every release test as evidence rather than treating an old result as a
  current verification.

### R0 — prove source feasibility before depending on it

- Test the actual Google Maps Demo Key account without billing for place lookup,
  maps, routes and transit across ten geographic cases. Verify quotas, dates,
  attribution, retention and coverage restrictions.
- Treat Delhi GTFS as regional and usable only after its terms and freshness are
  verified. Consider Mappls only as a verified replacement if Google is unsuitable.
- Select one viable source stack; do not build parallel integrations. Do not assume
  free national train, bus or flight inventory exists.
- Surface source coverage as `supported`, `not_covered`, `temporarily_unavailable`,
  `unknown`, or `manual`. Source-independent work may continue, but an unverified
  integration does not pass this gate.

### R1 — build the generic, evidence-aware domain

- Separate real and demo trips, plus editable drafts and active itineraries.
- Keep transport graph, physical route, semantic dependency DAG and alternative
  plans as distinct concepts. Model service patterns, calendars, exceptions, runs,
  ordered stop calls, scheduled/observed times, multi-day travel and goals.
- Store fact provenance, evidence and freshness. Model money as exact/range/unknown
  paise with party and scope, and keep sunk cost, cash due now and unreceived refund
  separate. Do not assume seats, accessibility or vehicle facts.
- Use one evaluator for impact, planning and adoption. It must distinguish structural
  errors, missing facts and known infeasibility; processing deadlines are not slack,
  and a delay cannot move a fixed cutoff.
- Introduce versioned SQLite migrations, immutable history and a legacy reader with
  explicit conversion. Preserve old hashes and stale-state protection.

### R2 — create and manage trips

- Add saved-trip and demo entry points. Support Travel, Stay, Activity, Deadline
  and Free-time items; train, flight, bus, local transit, car, walk and manual ferry;
  and search, pin, coordinate or manual places.
- Capture dates, party, budget and activity constraints. Support draft save/reopen
  and non-mutating validation; keep editing a draft separate from changing an active
  itinerary.
- Regenerate sequential connections while preserving hard dependencies and the past
  prefix. Require acknowledgement for hard implications and reject stale responses.

### R3 — recover from disruption

- Fetch external facts through adapters before pure-domain evaluation. Normalize
  walking/transit chains and deduplicate runs and hubs.
- Start recovery from the traveler’s true position and time, including future stops
  while onboard or a flight landing. Request missing facts instead of inventing them.
- Make disruption updates idempotent absolute facts. Use a bounded priority-label
  search over waits, services, transfers and activity edits with explicit time,
  expansion and quota limits plus progressive widening.
- Compare only equivalent states for dominance; rank comparable cost, goals,
  changes, retention and buffer before pruning. Keep preset winners and unknown
  groups visible. Use stable semantic IDs and revisions.
- Persist queued, running, completed, partial, failed and cancelled planning jobs;
  provide worker, polling, cancellation and restart behavior.

### R4 — present understandable choices

- Use a real map only within provider terms, with a general SVG/list fallback.
- Synchronize map, timeline and cards. Show shared prefix and up to four visible
  branches, with a complete accessible list; expose cost, goals, slack and evidence.
- Use generic labels, explicit dates and estimated-progress disclosure. Preview is
  non-mutating; selection requires acknowledgement where appropriate.
- Support mobile, keyboard and reduced motion. Never imply a booking was executed.

### R5 — preserve truth and safe local data

- Use server wall-clock time for real trips and a distinct demo clock.
- Revalidate evidence expiry and versions without HTTP inside write transactions,
  then atomically recheck and commit. Adoption must be idempotent under retries and
  races.
- Allow an infeasible draft to be saved but never recommend it as valid. Require an
  acknowledgement for conditional options with unresolved facts.
- Bound provider failures; apply retention policy to persistence, logs and exports.
  Offline mode must never substitute synthetic facts for real data.
- Add versioned local export/import that omits restricted data. Keep server keys out
  of the browser and restrict any browser key to the minimum permitted surface.

### R6 — prove the complete experience

- Demonstrate the unfamiliar-trip flow end to end while retaining the demo.
- Test backup/restore and measure local-core latency separately from provider latency.
- Run a five-person comprehension check, prepare an honest pitch and a 1080p backup
  recording.
- Refresh code and documentation graph semantics, then record release evidence.

## Planned interfaces

Keep `/api/v1`; evolve the local frontend and backend together instead of adding a
second API. Future slices will extend trip creation and reads, add trip listing,
draft save and non-mutating validation, and apply an acknowledged draft through
itinerary adoption. They will add place/service search, transfer estimates and
source capabilities; extend events, constraints and state; and introduce planning
job creation/read/cancel, previews, adoption revision/expiry/idempotency,
import/export, and evidence retrieval.

Preserve the error envelope, version checks and demo reset. Regenerate OpenAPI,
TypeScript and examples with each implemented schema slice—never during a docs-only
change. Planned types include trip draft, calendars, stop records, evidence,
process rules, money, evaluation, coverage and jobs.

## Verification gates

| Phase | Required evidence |
| --- | --- |
| R0 | RTEST-25–28 and RTEST-32; source terms, quotas and coverage recorded |
| R1 | RTEST-02, 05, 08–20 and 22; migration/hash/history tests |
| R2 | RTEST-01, 03–07 and 10; draft, validation and stale-response tests |
| R3 | RTEST-08–09, 14–16, 21–26, 31 and 36; job/search/recovery tests |
| R4 | RTEST-35 and accessible end-to-end walkthrough |
| R5 | RTEST-27–34 and 38; concurrency, retention, export and offline tests |
| R6 | performance, backup/restore, usability and demo evidence |

Maintain controlled fixtures separately from actual provider records. Cover renamed
IDs, overnight/multi-day journeys, non-wedding goals, zero budgets, missing fares,
village routes, repeated hubs, hills and islands. Public hosting (RTEST-37) remains
deferred. Each future implementation slice must include behavior and contract tests,
documentation, evidence and a Graphify refresh before it is considered complete.

## Current-document consolidation record

| Previous material | Disposition | Preserved destination |
| --- | --- | --- |
| 01 product scope, 02 product requirements | Replaced with roadmap-aligned future specifications | Documents 01 and 02 |
| 06 technical architecture | Replaced with target modular architecture | Document 06 and `AI_CONTEXT.md` |
| 08 UX/demo specification | Replaced with generic-trip interaction specification | Document 08 and `DEMO_RUNBOOK.md` |
| 03 domain, 04 fixture, 05 algorithms, 07 contract, 09 tests | Retained as current-demo references | their updated authority notes |

The retained documents may describe behavior that the current code has not yet
implemented completely. Check the source and tests before making a completion claim.
