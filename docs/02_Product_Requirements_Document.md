# ResiliTrip — Product Requirements

**Document:** 02 of the ResiliTrip implementation set
**Status:** future requirements; current implementation remains the synthetic demo.
**Authority:** product boundaries come from Document 01; phase order and test gates come from `IMPLEMENTATION_PLAN.md`.

## User outcome

An unfamiliar traveler can answer: “Given where I really am, what I must reach, what I can spend, and what is known, which remaining plan is valid and why?” The answer must distinguish a safe recommendation from an option needing input or from an unavailable source.

## Primary journeys

1. **Create and check:** enter travel, stays, activities, deadlines or free time; select/search/pin/manual locations; provide dates, party, budget and constraints; save or validate without mutation.
2. **Reopen and edit:** reopen a saved draft or active trip, see its version and evidence freshness, and edit future items without rewriting completed history.
3. **Report disruption:** record an absolute delayed, cancelled, missed or changed fact; show downstream impact before recovery.
4. **Recover:** request bounded alternatives from current time/location, compare feasible and conditional choices, inspect evidence and rejected reasons, and preview without changing the active itinerary.
5. **Adopt and continue:** acknowledge an option’s hard implication or unknown condition, select it idempotently, and reopen retained selected history.

## Functional requirements

| Area | Requirement |
| --- | --- |
| Trip model | Support real/demo trips, drafts/active itineraries, full dates, multi-day travel, party, budget, goals and explicit constraints. |
| Items | Support Travel, Stay, Activity, Deadline and Free-time; train, flight, bus, local transit, car, walk and manual ferry. |
| Facts | Store scheduled/observed facts, source/evidence/freshness, exact/range/unknown money, availability and accessibility without guessing. |
| Validation | Return structural errors, missing facts and known infeasibility separately; validation is non-mutating. |
| Continuity | Recovery begins at actual time/location/boarding state; past and onboard prefixes are retained. |
| Search | Use bounded inspectable search with waits, transfers, services and permitted activity edits; preserve alternatives and explain pruning. |
| Ranking | Rank only comparable candidates after feasibility; expose cost, goals, change, retention and buffer trade-offs. |
| Jobs | Persist queued, running, completed, partial, failed and cancelled planning jobs; support polling, cancellation and restart handling. |
| Selection | Preview does not mutate; selection rechecks evidence/version, requires acknowledgement when needed, and is retry-safe. |
| Data control | Support versioned local export/import with restricted-data omission and retention enforcement. |

## Experience, quality and safety

- Show current position, next action, commitments and health before technical detail. Keep map, timeline, cards and accessible list synchronized to one backend snapshot.
- Display source, freshness, estimate/unknown state, cost scope, deadline impact and reason before encouraging a choice. Never imply an external booking occurred.
- Support keyboard navigation, mobile layouts, reduced motion and a non-map path. The demo entry remains visibly synthetic/not-bookable.
- A draft may be infeasible but cannot be advertised as a valid recommendation. No provider call occurs inside a SQLite write transaction. Real trips use server wall-clock time; demos use a separate clock.
- Offline mode may show stored facts and manual entry but never invent real data. Browser clients never receive unrestricted server credentials.

## Acceptance mapping

Implement in roadmap order: R0 source feasibility; R1 domain/migrations; R2 trip creation; R3 recovery/jobs; R4 presentation; R5 safety/export; R6 end-to-end proof. RTEST mappings and controlled fixture cases are normative in `IMPLEMENTATION_PLAN.md`; Document 09 owns concrete test evidence.
