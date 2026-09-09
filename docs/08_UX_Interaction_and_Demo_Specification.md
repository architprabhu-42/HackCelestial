# ResiliTrip — UX, Interaction and Demo Specification

**Document:** 08 of the ResiliTrip implementation set
**Status:** target interaction specification; the current UI remains the synthetic Mumbai–Goa demo until corresponding roadmap slices are implemented.
**Authority:** Documents 01 and 02 define product meaning; Document 06 defines backend authority; `IMPLEMENTATION_PLAN.md` defines implementation order.

## Experience promise

Within the first screen, a traveler can understand where they are, what comes next, what commitments remain and whether action is needed. After a disruption they can understand the impact, the evidence behind every option, and what selecting an option changes—without interpreting an internal graph or provider jargon.

## Information architecture

| View | Purpose |
| --- | --- |
| Entry | Choose a saved trip, create a trip, or open the clearly separate synthetic demo. |
| Trip editor | Create/edit a draft with items, locations, dates, party, budget and constraints. |
| Validation | Present structural issues, missing facts and known infeasibility without mutating the trip. |
| Journey workspace | Show current state, remaining timeline, map/list, commitments, evidence and health. |
| Disruption and impact | Capture an absolute service fact and show affected downstream items. |
| Recovery | Show feasible, conditional and rejected alternatives with filters and explicit reasons. |
| Preview/select | Compare a proposed plan with active history, require acknowledgement where needed, then select. |
| Sources and data | Show source capability/freshness and local export/import controls. |

## Interaction rules

- Create mode accepts place search, map pin, coordinates or manual names. A source failure never prevents manual entry; it is visibly marked.
- Edits to future draft items validate through the server. Edits that alter a hard dependency or active future itinerary show consequences and need explicit acknowledgement.
- Reporting a delay, cancellation, missed service or other fact creates an idempotent absolute event. The result shows affected state before search.
- Recovery shows a shared prefix and up to four visible branches plus a complete accessible list. A conditional option shows what is unknown and what the traveler must acknowledge; a rejected option shows its reason.
- Preview is non-mutating. Selection names retained/dropped items, cash due now, evidence freshness, version and conditional acknowledgement. A stale result refreshes instead of being silently applied.

## Presentation and language

Use generic wording for real trips, explicit dates for multi-day journeys, and plain language for deadline, cost, buffer and uncertainty. Show exact/range/unknown money with scope; never turn unknown into zero. The UI may link to a provider but must never say a provider action occurred.

Map, timeline, cards and list are views of the same backend snapshot. If a map or provider route is unavailable, show a fully usable ordered list/SVG fallback rather than a blank or misleading map. Show source and freshness alongside external facts.

## Accessibility and resilience

- Every map/branch/motion view has an equivalent semantic list or table.
- Support keyboard-only navigation, focus restoration, readable errors, mobile layouts and reduced-motion preferences.
- Never rely on color alone for feasible, conditional, unavailable or rejected state. Preserve interaction state across polling and recoverable provider errors.
- Disable only the action that is unsafe; keep manual entry, inspection and export available where possible.

## Demo requirements

The Mumbai–Goa demo remains a reliable, offline, non-bookable walkthrough for the current baseline. Its script is in `DEMO_RUNBOOK.md`. It is visually and semantically separated from real-trip creation, including source, clock, data and disclosure. Demo-only fixture values never appear as claims about real provider availability.

## UI acceptance

Before R4 is complete, prove a keyboard and mobile traveler can create/validate a trip, report a disruption, inspect evidence/reasons, preview, acknowledge and select an option, and reopen the result. Prove list/SVG fallback and the synthetic demo remain usable without map/provider access. Record RTEST-35 walkthrough and R6 comprehension evidence defined in the roadmap.
