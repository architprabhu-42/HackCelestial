# ResiliTrip — Product Decision and Scope

**Document:** 01 of the ResiliTrip implementation set
**Status:** adopted product direction; no feature described here is implemented unless code and fresh evidence say so.
**Authority:** `IMPLEMENTATION_PLAN.md` controls sequencing and delivery gates. This document controls durable product decisions and claim boundaries.

## Product decision

ResiliTrip is a local-first trip-planning and disruption-recovery application. A traveler can create an unfamiliar trip, check it, save and reopen it, report a disruption, compare recovery options, preview and select one, then reopen the result. The product must state missing, estimated and unavailable facts plainly.

The Mumbai–Goa scenario stays as a separate demo mode. It is synthetic, non-bookable, and must never be represented as real inventory or a provider action. The current application implements only that demo baseline.

## Decisions that implementation must preserve

| Decision | Required outcome |
| --- | --- |
| Local first | The core works on one local installation with React/TypeScript, FastAPI/Python and SQLite. |
| Free only | A source is used only after free access, terms, coverage, quota, attribution and retention are verified. |
| Truth before convenience | Unknown, stale, estimated and unsupported facts remain visible; no synthetic substitute is used for a real trip. |
| Decision support | No booking, cancellation, payment, refund or provider-side change occurs. |
| One domain authority | Backend evaluation owns feasibility, time, money, ranking, plan identity and versions. |
| Real/demo separation | Demo data, clocks, labels and history cannot silently become real-trip data. |
| Feasibility before ranking | A known-invalid plan is never recommended; conditional plans require acknowledgement. |
| Evidence-aware history | Versions, evidence, source freshness and selected-plan history are retained locally. |

## Scope boundaries

In scope: itinerary creation; manually entered places and legs; verified source lookups where available; stays, activities, deadlines and free time; disruption reporting; bounded recovery search; save/reopen; evidence display; accessible map or list rendering; local import/export subject to retention rules.

Out of scope: payment, booking/cancellation execution, PNR management, provider refund processing, autonomous booking agents, live weather/ML/chat, public hosting, and self-hosted national transport inventory.

## Source-feasibility rule

R0 is a gate, not an implementation detail. Before a provider capability becomes required behavior, record the tested account, date, product/API, region, quota, terms, attribution, retention, fallback and observed result. Use `supported`, `not_covered`, `temporarily_unavailable`, `unknown`, and `manual` consistently.

Google Maps Demo Key capability must be verified with the actual account and no billing. Delhi GTFS is regional only. Mappls is considered only as a verified replacement, not a parallel stack. Do not claim free national train, bus or flight data without evidence.

## Completion claims

Do not call a roadmap phase complete because a screen exists. Completion requires the phase’s contract and behavior tests, source/evidence records where applicable, documentation, and a Graphify refresh. The final product claim requires the full non-demo flow, retained demo flow, backup/restore, performance evidence and R6 comprehension/demo evidence.

## Document order

`IMPLEMENTATION_PLAN.md` is first for work ordering. Documents 02, 06 and 08 turn this product decision into requirements, architecture and interaction behavior. Documents 03, 04, 05, 07 and 09 retain the current-demo baseline and evolve in versioned slices; they must not block the generic-trip direction.
