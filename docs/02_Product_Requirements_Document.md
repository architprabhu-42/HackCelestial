# ResiliTrip — Product Requirements Document

**Document:** 02 of the ResiliTrip implementation pack  
**Version:** 1.0  
**Date:** 6 September 2026  
**Status:** Proposed; becomes implementation baseline after Document 01 is locked  
**Product:** ResiliTrip — India-first Travel Disruption Recovery  
**Event:** HackCelestial 3.0, PS2  
**Team:** Four undergraduate developers  
**Delivery window:** 24-hour finale

## 1. Document purpose and authority

This PRD defines what the HackCelestial version of ResiliTrip must do, what users must understand, and how the team will decide that the product is complete. It translates the audited research and scope decisions into user stories, functional requirements, interface states, success measures and release gates.

Source precedence:

1. `01_Product_Decision_and_Scope_Lock.md` controls product scope and approved changes.
2. This PRD controls product behavior and acceptance.
3. `PS2_Travel_Disruption_Recovery_Dossier.md`, Revision 2, supplies research evidence and corrected calculations.
4. Later domain, fixture, algorithm, architecture, API, UX and test documents provide implementation detail without changing the product boundary.

If a later document conflicts with Document 01 or this PRD, the team must resolve the conflict through the scope change process before coding the disputed behavior.

## 2. Product summary

ResiliTrip helps an Indian traveler understand and recover from a disruption across separately booked parts of a journey. The traveler supplies an itinerary, current location, current time and constraints. The product models relationships among transport, transfers, hotel check-in and an important event. When a service is delayed or cancelled, it shows the downstream effect and generates feasible recovery plans from a bounded scenario catalog.

The HackCelestial product is a transparent simulation. It demonstrates recovery reasoning with fictional schedules, prices, capacity and policies. It does not purchase, cancel or modify external bookings. The persistent primary label is `SYNTHETIC SCENARIO — NOT BOOKABLE`.

### Product promise

> Given where I am, what I must reach and how much I can spend, show what breaks and which recovery plans still satisfy my constraints.

### Product distinction

The main product value is the combination of:

- a visible dependency chain from disruption to affected commitment;
- recovery that begins from the traveler’s actual current state;
- hard validation of time, location, capacity and money;
- generated alternatives with rejected-option explanations;
- clear separation between a proposed plan and a completed booking.

The moving route animation supports this experience. It is not the central product capability.

## 3. Problem and opportunity

Travelers often hold separate bookings for trains, flights, local transfers, hotels and events. A disruption in one item requires them to determine which later commitments remain reachable, find alternatives, compare additional cash, understand lost bookings and decide quickly. Information lives across providers, and separate tickets rarely form one protected journey.

Existing itinerary and enterprise disruption products establish that alerts and recovery are valuable. For this prototype, the opportunity is to make the reasoning inspectable for an Indian multimodal journey while remaining honest about unavailable provider inventory and legal-policy certainty.

The product addresses four immediate user questions:

1. **What is affected?** Show the causal path and before/after timing.
2. **What can I still do?** Return only plans that meet the selected hard constraints.
3. **What will it cost now?** Separate cash required, incremental cost and uncertain refunds.
4. **What happens after I choose?** Update the proposed itinerary and list external actions still required.

## 4. Goals and non-goals

### P0 goals

| Goal ID | Goal | Evidence of success |
|---|---|---|
| G01 | Explain downstream disruption impact | User opens a causal chain and sees the exact activity, cutoff, readiness and slack |
| G02 | Generate feasible recovery choices | Hero catalog produces F2 and F3 from atomic services and transfers |
| G03 | Reject impossible or unaffordable choices | Waiting and F4 are rejected; budget changes remove plans deterministically |
| G04 | Make trade-offs understandable | Cards expose cash, incremental cost, arrival, slack, changed bookings and source labels |
| G05 | Keep the traveler in control | User selects ranking preset, edits constraints and explicitly adopts a plan |
| G06 | Maintain truthful simulation claims | Synthetic and not-bookable labels stay visible through setup, comparison and adoption |
| G07 | Deliver a reliable interactive demo | Core scenario works repeatedly without external status, routing or map services |
| G08 | Demonstrate India-specific reasoning | Typed stations/airports, IST, INR, separate tickets and policy uncertainty affect behavior |

### P1 goals

After P0 is stable and recorded, the approved stretch pool includes minimum budget relaxation, a second Indian corridor, richer input import, language templates, duration ranges, specific onboard recovery, accessibility data, an authorized status adapter and optional natural-language assistance.

### Non-goals

- Executing bookings, payments, cancellations, refunds, compensation or TDR requests.
- Claiming live inventory, fare availability or nationwide route coverage.
- Scraping Indian transport or travel websites.
- Providing legal entitlement calculations.
- Managing groups, split parties, children or emergency travel.
- Optimizing airline aircraft, crew, gates or network operations.
- Building a provider marketplace or operational dashboard.
- Predicting disruption probability.
- Making an LLM responsible for schedules, prices, policies, feasibility or ranking.

## 5. Persona and usage context

### Primary persona: Asha

| Attribute | Definition |
|---|---|
| Situation | Traveling from Mumbai to Goa using separately arranged train, cabs and hotel |
| Critical commitment | Wedding starts at 19:30; required arrival by 19:15 |
| Disruption | Train delay becomes known before boarding at CSMT |
| Current state | Outside CSMT at 05:00, not boarded |
| Constraints | One traveler, ₹10,000 cash limit, ₹9,000 maximum incremental cost, hotel visit required |
| Main concern | Preserve the wedding while understanding the immediate financial effect |
| Trust need | Know which inputs are synthetic, estimated or user-reported and why each option passes or fails |

### Job to be done

When an important leg changes, Asha wants to see how it affects the rest of her trip and choose a physically and financially feasible recovery plan without mistaking a suggestion for a completed booking.

### P0 accessibility and language context

The interface is English and must remain usable with keyboard navigation, visible focus, text labels in addition to color, reduced motion and a non-map itinerary table. The hero does not assert a traveler accessibility requirement. If a manual trip says accessibility is required and the relevant facts are unknown, the product must not certify the plan.

## 6. Assumptions and constraints

| ID | Assumption or constraint | Product implication |
|---|---|---|
| A01 | P0 runs in demo mode with fictional data | All journey and recovery claims carry simulation labels |
| A02 | One adult traveler | Party sizes other than one are rejected in P0 |
| A03 | Maximum 20 activities and 50 service instances | Search and rendering stay bounded; larger inputs receive validation errors |
| A04 | Recovery horizon is 24 hours | Results apply only to that time window |
| A05 | Hero begins before train boarding | CSMT-origin recovery is physically valid in the fixture |
| A06 | Fixed services change only through their own event | Traveler lateness creates a missed connection rather than moving the service |
| A07 | Required unknown facts fail certification | Product returns unknown/needs-input instead of optimistic assumptions |
| A08 | External providers are not integrated | Adoption changes only ResiliTrip’s proposed itinerary |
| A09 | Unreceived refunds cannot fund recovery | Cash validation excludes potential refunds |
| A10 | Map services may be unavailable | Graph, table and local illustrative route remain functional |
| A11 | Official refund sources have unresolved applicability conflicts | P0 shows verification guidance rather than entitlement amounts |
| A12 | Team has 24 hours and four developers | P0 requirements take priority over stretch features and provider integration |

### Reference outputs for product acceptance

The detailed atomic services and transfer calculations belong in the fixture specification. This PRD locks the user-visible results that those inputs must produce:

| Candidate | Cash still required | Increment above ₹1,300 | Venue arrival | Wedding slack | Product treatment |
|---|---:|---:|---|---:|---|
| Wait for delayed T1 | ₹1,300 | ₹0 | 20:50 | −95 min | Rejected by hard deadline |
| F2 through GOX | ₹9,700 | ₹8,400 | 13:35 | +340 min | Feasible; first under fastest |
| F3 through GOI | ₹6,500 | ₹5,200 | 17:20 | +115 min | Feasible; first under cheapest |
| F4 through GOX | ₹5,700 | ₹4,400 | 20:05 | −50 min | Rejected by hard deadline |

These outputs are scenario expectations, not current fare or availability claims.

## 7. End-to-end user journey

### Journey 1 — Load and inspect the original trip

1. User enters demo mode and loads `mumbai-goa-v2`.
2. Product displays a persistent synthetic/not-bookable banner.
3. User reviews current time, location, boarding state, budget and hard commitments.
4. Product displays the original journey in a table, dependency graph and map preview.
5. Product shows that the baseline reaches the venue at 17:50 with 85 minutes of slack.

### Journey 2 — Apply and understand a disruption

1. User triggers the three-hour T1 timing update.
2. Product applies the event once and advances the trip version.
3. Flexible downstream activities move according to their windows; the wedding does not move.
4. Product shows venue arrival at 20:50 and negative 95 minutes of slack.
5. User selects the affected wedding and sees the causal path from T1 through exit, cab, hotel and final transfer.
6. Hotel remains valid because its latest check-in start is 21:00.

### Journey 3 — Generate and compare recovery

1. User requests plans using the default `cheapest` preset.
2. Product searches the configured atomic catalog under current constraints.
3. F3 ranks first and F2 remains available; F4 and waiting appear in the rejected section.
4. User compares cash required, incremental cost, venue arrival, slack and changed bookings.
5. User opens “Why not F4?” and sees that arrival is 50 minutes after the hard cutoff.

### Journey 4 — Change a constraint

1. User changes cash limit to ₹7,000.
2. Product creates a new trip version, invalidates old previews and regenerates when requested.
3. F3 remains; F2 is rejected for exceeding cash.
4. If cash changes to ₹5,000, product reports no feasible plan in the evaluated catalog.

### Journey 5 — Adopt and hand off

1. User selects F3 and acknowledges that it is simulated.
2. Product revalidates the current versions and constraints.
3. Product creates an adopted proposed itinerary.
4. Product states that no external booking was executed and keeps original booking status unchanged.
5. Product shows actions to verify real service availability, fare conditions and original-booking options with providers.

### Journey 6 — Reset and repeat

1. User resets the scenario.
2. Product restores the original fixture under a new version.
3. All previous plan previews become stale.
4. The baseline calculations and demo can be repeated without restarting the application.

## 8. User stories

| Story ID | User story | Priority | Acceptance summary |
|---|---|---|---|
| US01 | As a traveler, I want to load or enter my connected itinerary so I can see the whole remaining journey | P0 | Valid trip loads; invalid fields identify the correction needed |
| US02 | As a traveler, I want to state where I am and whether I have boarded so suggestions start from reality | P0 | Current state changes eligible paths; onboard user is not returned to CSMT |
| US03 | As a traveler, I want to see dependencies so I know why one delay affects later commitments | P0 | Graph/table reveal causal path without relying on color alone |
| US04 | As a traveler, I want to replay a delay or cancellation so I can evaluate changed circumstances | P0 | Event applies once; unsupported disruption types are rejected clearly |
| US05 | As a traveler, I want to see which commitments remain feasible, risky, blocked or impossible | P0 | Status and exact slack/reason are visible |
| US06 | As a traveler, I want several valid recovery choices when they exist | P0 | Plans are generated from atomic records and validated against all hard constraints |
| US07 | As a traveler, I want rejected choices explained so I can trust that cheaper does not mean possible | P0 | F4 and waiting show exact failed constraint and observed/required values |
| US08 | As a traveler, I want to compare fastest, cheapest and fewest-changes results | P0 | Presets reorder the same valid set deterministically |
| US09 | As a traveler, I want to change my budget and see the plans update | P0 | New version invalidates previews and changes feasible set correctly |
| US10 | As a traveler, I want cash, sunk cost and possible refund separated | P0 | Unknown refund never reduces cash required |
| US11 | As a traveler, I want to adopt a plan without being misled about booking status | P0 | Explicit acknowledgement; response says no booking occurred |
| US12 | As a presenter, I want to reset and operate offline so the demonstration is repeatable | P0 | Core flow works with network disabled and returns to known fixture state |
| US13 | As a traveler with no feasible plan, I want to know which constraint blocked recovery | P0 | No-solution result lists evaluated scope and blockers |
| US14 | As a traveler, I want to know the source and freshness of important facts | P0 | Field-level provenance remains available in comparison and detail views |
| US15 | As a traveler, I want the smallest budget increase that enables a valid plan | P1 | Only cash relaxes; result requires explicit constraint update and rerun |

## 9. Functional requirements

The requirement IDs below are stable. Later design and implementation work must refer to them in commits, tasks and tests.

### 9.1 Trip creation and current state

| FR ID | Requirement | Acceptance criteria | Trace |
|---|---|---|---|
| FR-001 | Load a versioned fixture by scenario ID | `mumbai-goa-v2` loads all activities, services, transfers, constraints, financial baseline, policies and provenance; unknown scenario returns a clear error | P0-01, R01 |
| FR-002 | Accept a manual structured itinerary | User can enter one traveler, activities, times, locations, dependencies, constraints and sources; product rejects missing timezones, duplicate IDs, invalid windows, graph cycles and bounds violations | P0-02, R01 |
| FR-003 | Require current-state input | Current time, typed location and phase are present before impact/recovery; onboard phase requires an active service and modeled next recovery point | P0-03, R01/R05 |
| FR-004 | Review assumptions before calculation | Setup review lists hard commitments, budgets, fictional policies and source classes; user can return to edit | P0-02/P0-03, R10 |

### 9.2 Journey representation

| FR ID | Requirement | Acceptance criteria | Trace |
|---|---|---|---|
| FR-005 | Display connected itinerary | Table and graph represent the same ordered activities/dependencies; selecting an item synchronizes its detail across views | P0-04/P0-19, R02 |
| FR-006 | Display baseline timing | Hero baseline shows venue arrival 17:50 and +85-minute slack; source and scenario labels remain visible | P0-07/P0-14, R02/R10 |
| FR-007 | Provide a map-independent journey view | All times, statuses, costs and reasons remain understandable in the itinerary table when map rendering is absent | P0-20, R12 |

### 9.3 Disruptions and impact

| FR ID | Requirement | Acceptance criteria | Trace |
|---|---|---|---|
| FR-008 | Apply an absolute service timing update | D1 changes T1 to 09:00–18:30 once; identical retry does not add another delay or version | P0-05, R03 |
| FR-009 | Apply a service cancellation | Cancelled service becomes unavailable and cannot appear in a valid path; dependent original chain becomes blocked until recovery | P0-06, R03/R04 |
| FR-010 | Reject unsupported disruption semantics | Weather/gate payloads unsupported in P0 return validation guidance; they are not converted into guessed delays | P0-18, R03/R11 |
| FR-011 | Propagate flexible activities only | Cab/check-in can move within declared windows; fixed services and hard events remain fixed unless explicitly updated | P0-07, R04 |
| FR-012 | Calculate status and slack | Negative hard slack is infeasible; 0–29:59 is at risk; at least 30 minutes is feasible under known inputs; unknown required facts produce unknown | P0-07/P0-08, R04/R08 |
| FR-013 | Explain causal impact | Affected activity detail shows root event, causal activities, readiness, cutoff, slack and reason codes; hero delay reaches 20:50 with −95 minutes | P0-07/P0-10, R02/R04 |

### 9.4 Recovery generation and comparison

| FR ID | Requirement | Acceptance criteria | Trace |
|---|---|---|---|
| FR-014 | Generate paths from atomic services and transfers | Hero search constructs F2/F3/F4/wait paths from catalog items; finished plan cards are not the source of truth | P0-09, R05 |
| FR-015 | Validate all hard constraints | A certified plan passes current location/time, service cutoff/status, known capacity, required windows, cash, extra cost, mode and commitment deadline | P0-09/P0-10, R05 |
| FR-016 | Return the honest number of plans | Product may return 0–3 frontier plans; it never fabricates a third valid choice | P0-09/P0-18, R05/R11 |
| FR-017 | Rank valid plans by preset | Fastest selects F2; cheapest selects F3; fewest-changes uses declared deterministic tie-breakers; hard constraints are never weights | P0-11, R05/R06 |
| FR-018 | Show accepted and rejected options separately | Rejected item identifies failed constraint, observed value and required value; F4 shows arrival 20:05 versus 19:15 cutoff | P0-10, R06 |
| FR-019 | Report search scope and completeness | Result includes catalog version, horizon, bounds and complete/partial/needs-input status; copy never generalizes beyond evaluated catalog | P0-18/P0-22, R11 |
| FR-020 | Recompute after constraint changes | Budget edit creates a new version and invalidates prior plans; ₹7,000 leaves F3; ₹5,000 yields no feasible catalog plan | P0-12/P0-16, R05/R07/R11 |

### 9.5 Money and policy

| FR ID | Requirement | Acceptance criteria | Trace |
|---|---|---|---|
| FR-021 | Display immediate cash requirement | F3 line items total ₹6,500 and appear in INR formatting; repeated graph references do not duplicate charges | P0-13, R06/R09 |
| FR-022 | Display incremental cost separately | F3 shows ₹5,200 above frozen ₹1,300 remaining baseline; already-paid train/hotel appear as context | P0-13, R06/R09 |
| FR-023 | Keep refunds out of cash validation | Unknown potential refund is displayed as unknown and does not reduce cash; refund, compensation and assistance have distinct labels | P0-13/P0-21, R09 |
| FR-024 | Limit policy calculation to fictional terms | Scenario policy may calculate declared fictional fee/refund fields; official links produce verification guidance without guaranteed entitlement | P0-21/P0-22, R09/R10 |

### 9.6 Plan adoption and lifecycle

| FR ID | Requirement | Acceptance criteria | Trace |
|---|---|---|---|
| FR-025 | Require simulation acknowledgement | Adopt control remains disabled until user acknowledges the plan is synthetic and not bookable | P0-15/P0-22, R07/R10 |
| FR-026 | Revalidate before adoption | Server checks trip version, catalog version, current state, plan validity and hard constraints; stale plan returns conflict | P0-15/P0-16, R07 |
| FR-027 | Adopt internally | Successful adoption creates a new proposed itinerary version, preserves original booking states and returns `external_booking_executed:false` | P0-15, R07 |
| FR-028 | Expire plans | Relevant event/constraint/current-state change or validity cutoff marks preview stale; stale plan cannot be adopted | P0-16, R07 |
| FR-029 | Provide provider-handoff checklist | Adoption screen lists service availability, fare/policy and original-booking verification actions; no action is reported as complete | P0-21, R09 |

### 9.7 Reliability, reset and truth labels

| FR ID | Requirement | Acceptance criteria | Trace |
|---|---|---|---|
| FR-030 | Reset scenario safely | Reset restores original fixture content under a new monotonically increasing version; old plans remain stale | P0-17, R12 |
| FR-031 | Distinguish product states | UI differentiates ready/loading/complete/no-feasible-plan/needs-input/partial-search/stale/error/offline; each supplies an appropriate next action | P0-18, R11/R12 |
| FR-032 | Maintain persistent truth labels | Synthetic/not-bookable labels appear on setup, journey, comparison and adoption; source badges appear on relevant fields | P0-14/P0-22, R10 |
| FR-033 | Operate core flow offline | With network disabled, fixture load, event, impact, recovery, graph/table, local route, adoption and reset work | P0-20, R12 |
| FR-034 | Keep views consistent | Map, graph, table and cards render the same trip version; stale mixed-version content is not shown as current | P0-19, R02/R07/R12 |

## 10. Product states and user-facing behavior

| State | Trigger | Required presentation | Allowed action |
|---|---|---|---|
| `setup` | No valid trip | Form/fixture choice and validation | Load or create trip |
| `ready` | Valid baseline | Journey and baseline metrics | Apply event or edit constraints |
| `loading` | Mutation/search active | Preserve last good view, progress indicator, disable repeated action | Cancel only if safely supported; otherwise wait |
| `impacted` | Event applied | Changed statuses, causal impact and recovery prompt | Generate plans |
| `complete` | Search completed | Valid frontier plans, rejected summary and search scope | Compare, edit constraints or adopt |
| `no_feasible_catalog_plan` | Complete bounded search finds zero valid paths | Failed constraints, evaluated scope and reset/edit actions | Edit constraints or reset |
| `needs_input` | Required fact missing | Name missing facts and affected checks | Correct current state/input |
| `partial_search` | Bound/timeout interrupts search | Partial label, limits reached and no global-optimum claim | Retry with controlled bounds or use available labeled results without “best” claim |
| `stale` | Preview version/validity no longer current | Stale banner and explanation | Refresh/regenerate; adoption disabled |
| `adopted` | Current valid plan accepted | Proposed itinerary, unchanged booking state and checklist | Preview route, return to journey or reset |
| `offline` | External map/service unavailable | Local route/table/graph and explanation that core demo continues | Continue core flow |
| `error` | Infrastructure failure | Clear retryability and preserved state | Retry or reset according to error |

No-solution, missing-input and system-error states must not use the same message.

## 11. Business rules visible to product and QA

| Rule ID | Rule |
|---|---|
| BR-01 | A hard commitment with negative slack makes that candidate infeasible, even by one second |
| BR-02 | Slack from zero through less than 30 minutes is at risk; 30 minutes is the initial safe threshold |
| BR-03 | The 30-minute threshold is a configurable heuristic, not a probability or guarantee |
| BR-04 | A fixed service changes only through an event for that service |
| BR-05 | Cancellation makes a service unavailable; it is not represented as a large delay |
| BR-06 | Recovery starts at current time/location/state and preserves completed or active history |
| BR-07 | Required unknown capacity/accessibility/time/fee prevents certification |
| BR-08 | Hard validation happens before ranking |
| BR-09 | At most three distinct Pareto-frontier plans are shown in the primary comparison |
| BR-10 | Cheapest sorts by cash required first; fastest sorts by arrival first; fewest changes sorts by changed-booking count first |
| BR-11 | Cash and incremental-cost limits are checked independently |
| BR-12 | Unreceived refunds never reduce cash required |
| BR-13 | Each financial item is counted once by unique ID |
| BR-14 | Plan adoption never changes an external booking state |
| BR-15 | A result may claim completeness only inside the declared catalog, horizon and bounds |
| BR-16 | Every computed fact shown in multiple views refers to the same trip/catalog version |

Detailed graph, timing, search and financial formulas belong in Documents 03–05. Those documents must preserve these observable rules.

## 12. Screen-level product requirements

### 12.1 Setup and review

Must show scenario/manual choice, traveler count, current time, typed location, boarding phase, budget, incremental-cost limit, required hotel/event and data-source labels. Manual input may use sections or a guided sequence. The user must review assumptions before calculations begin.

### 12.2 Journey workspace

Must show a synchronized itinerary table, dependency graph, map preview and version/source context. The table is the accessible fallback. Each item shows scheduled/effective time, location, status and source. A selected affected item reveals its causal explanation.

### 12.3 Replay controls

Must provide delay, cancellation, pause/step where animation uses time, and reset. The simulated clock is visible. A duplicate click cannot apply D1 twice. Unsupported event types are absent or clearly disabled.

### 12.4 Impact panel

Must identify root disruption, directly affected items, downstream commitments, before/after arrival, cutoff, slack and status. Hotel and wedding may have different results; the UI cannot color every later node identically merely because they share an upstream delay.

### 12.5 Recovery comparison

Must show valid plans first and rejected options separately. Each valid card includes route/modes, cash required, incremental cost, arrival, event slack, number of changed bookings, uncertainty/source badges and ranking reason. It must not show an unexplained composite score.

### 12.6 No-solution and needs-input

No-solution shows the evaluated scope and blocking constraints. Needs-input names the missing required facts. The ₹5,000 fixture displays no feasible catalog plan and may link to edit budget. P1 may compute the minimum cash limit; P0 does not silently change it.

### 12.7 Adoption and checklist

Must require simulation acknowledgement, show the selected proposed itinerary, state that no booking occurred, preserve original ticket states and list provider-verification actions. Do not use “confirmed,” “booked,” “refund approved” or equivalent success language for external actions.

## 13. Content and visual language

### Status vocabulary

Use exactly: `Feasible under scenario`, `At risk`, `Infeasible`, `Blocked`, `Unknown`, `Stale`, `Simulated`, `User reported`, `Estimate`, `Provider confirmed` and `Not bookable` where appropriate.

Color mapping may use green/amber/red/gray/blue, but every status also needs text or an icon with accessible label. Reduced-motion mode must stop nonessential marker movement without hiding state changes.

### Financial vocabulary

- **Cash still required:** money needed for remaining retained charges, new purchases and known required fees.
- **Above original remaining spend:** incremental amount over the frozen remaining baseline.
- **Already paid:** sunk context, shown separately.
- **Potential refund:** unknown or estimated future receipt; excluded from current cash.

### Prohibited claims

- Live tracking, live fare, available seat or provider-verified when sourced from a fixture.
- Guaranteed arrival or risk percentage.
- Nationwide best route or global optimum.
- Booking confirmed, cancellation completed or refund approved.
- Current legal entitlement derived from the fictional policy engine.

## 14. Non-functional requirements

| NFR ID | Requirement | Acceptance target |
|---|---|---|
| NFR-01 | Determinism | Same trip version, catalog version and preset produce identical ordered plans |
| NFR-02 | Performance | p95 impact plus search below one second over 100 warmed hero runs on recorded demo hardware; target until measured |
| NFR-03 | Responsiveness | Main interactions visibly respond within two seconds locally; target until measured |
| NFR-04 | Offline resilience | Core P0 passes with network disabled; no dependency on provider status or public map tiles |
| NFR-05 | Accessibility | Keyboard operation, focus visibility, non-color status, reduced motion and itinerary-table fallback |
| NFR-06 | Consistency | Authoritative values come from one backend snapshot/version |
| NFR-07 | Data integrity | Event/adoption mutation is atomic; duplicate/stale operations cannot corrupt state |
| NFR-08 | Privacy | P0 accepts fictional data and does not request PNR, Aadhaar, passport, email or payment data |
| NFR-09 | Input safety | Maximum 256 KB request, domain bounds, strict validation, escaped labels and allowlisted handoff destinations |
| NFR-10 | Recoverability | Reset returns known fixture content without reusing stale plan versions |
| NFR-11 | Explainability | Every feasibility/rejection outcome has structured reason codes and observed/required values |
| NFR-12 | Reproducibility | Clean checkout installation and launch documented after exact dependencies are tested and pinned |

## 15. Analytics and evaluation instrumentation

P0 analytics are local demo telemetry without personal identifiers. They support testing and the presentation; they are not product-market evidence.

| Event | Properties | Purpose |
|---|---|---|
| `scenario_loaded` | scenario ID, trip version | Confirm repeatable start |
| `disruption_applied` | event type, service ID, old/new version, applied/duplicate | Verify event behavior |
| `impact_viewed` | activity ID, status, causal depth | See whether explanations are inspected |
| `plans_generated` | result status, feasible count, rejected counts, elapsed ms, search complete | Validate planner and performance |
| `preset_changed` | from/to preset | Confirm comparison interaction |
| `constraint_changed` | field name, previous/new value, new version | Demonstrate adaptation without storing personal data |
| `rejection_opened` | plan ID, reason codes | Evaluate counterfactual explanation use |
| `plan_adopted` | plan ID, version, simulation acknowledged | Verify controlled adoption |
| `stale_adoption_blocked` | plan/trip versions | Verify protection |
| `scenario_reset` | previous/new version | Verify repeatability |
| `ui_error` | safe error code, screen, retryable | Diagnose demo failures |

Do not log names, unmasked booking references, arbitrary uploaded text or full external URLs.

## 16. Success metrics

### Hackathon readiness metrics

| Metric | Target before feature freeze | Evidence |
|---|---|---|
| Required hero calculations | 100% match with reference fixture | Automated fixture tests |
| Hard-constraint safety tests | 100% pass | T01–T22 subset mapped in test strategy |
| Repeat demo success | 5 consecutive complete runs | Runbook checklist/video |
| Offline core | Complete journey works with network disabled | Recorded test |
| Mixed-version UI defects | 0 observed in required flow | End-to-end test |
| Synthetic-label coverage | 100% of required screens | UX review |
| Unfamiliar-user comprehension | 5/5 identify cheapest plan, F4 failure and no booking | Short observed usability check |

### Metrics that must not be claimed from this prototype

- Percentage reduction in real traveler disruption cost.
- Accuracy of real delay prediction.
- Real booking conversion or recovery success.
- Refund-eligibility accuracy.
- National route coverage.
- Statistical user-satisfaction improvement.

## 17. Dependencies and risks

| Risk ID | Risk | Impact | Product response |
|---|---|---|---|
| RK-01 | Team builds polished hardcoded cards | Core recovery claim fails scrutiny | Require FR-014 and fixture-level generation before visual polish |
| RK-02 | Planner and impact view disagree | User cannot trust explanations | One shared evaluator; contract and golden tests |
| RK-03 | Current location omitted | Physically impossible recommendations | FR-003 and onboard adversarial test |
| RK-04 | Financial values double-count or use refund | Invalid budget decisions | Unique money items and FR-021–023 tests |
| RK-05 | Map or network fails during judging | Demo interruption | FR-007/033 and local geometry fallback |
| RK-06 | Simulation looks deceptive | Credibility loss | Persistent truth labels and adoption wording |
| RK-07 | Scope expands to integrations/LLM | P0 remains incomplete | Scope lock, stop rules and P1 entry gate |
| RK-08 | Plan becomes stale during interaction | Invalid adoption | Versioning, validity cutoff and server revalidation |
| RK-09 | Official policy sources conflict | Misleading refund claim | No statutory calculator; provider verification guidance |
| RK-10 | Component versions fail together | Lost implementation time | Test/pin exact dependencies early; retain minimal fallbacks |
| RK-11 | Official event deadline/prebuild rule remains unclear | Submission or eligibility issue | Team lead obtains organizer confirmation immediately |

External provider APIs are not P0 dependencies. React Flow, NetworkX, MapLibre, FastAPI, Pydantic and SQLite are intended components subject to the later architecture document and a clean compatibility trial.

## 18. Release and demo gates

### Gate 1 — Product baseline

- Document 01 locked by team.
- This PRD approved.
- Roles A–D assigned.
- Organizer clarification requested for pre-event development and conflicting deadline.

### Gate 2 — Headless correctness

- Reference fixture loads.
- Baseline, D1, F2/F3/F4/wait and budget calculations pass.
- Duplicate events, negative/zero slack, capacity and current-state cases pass.

### Gate 3 — Integrated P0

- Required screens use backend snapshots.
- Generated comparison, rejection detail, adoption, stale protection and reset work.
- Truth labels and provider checklist are present.

### Gate 4 — Demo reliability

- Clean build and launch documented.
- Five consecutive main-flow runs succeed.
- Offline core succeeds.
- Backup video recorded.
- At least five-person comprehension check completed.
- Third-party notices and map attribution reviewed.

Only after Gate 4 may the team start a P1 feature. From hour 21, only defect fixes are allowed.

## 19. Traceability matrix

| Dossier requirement | PRD functional requirements | Scope capabilities | Primary acceptance evidence |
|---|---|---|---|
| R01 Input | FR-001–004 | P0-01–03 | T01 |
| R02 Connected trip | FR-005–007, FR-013 | P0-04/P0-07/P0-19 | T02–T03 |
| R03 Disruption | FR-008–010 | P0-05/P0-06 | T04/T19 |
| R04 Impact | FR-011–013 | P0-07/P0-08 | T03/T05–T07 |
| R05 Recovery | FR-014–020 | P0-09–12 | T08–T11/T16 |
| R06 Comparison | FR-017–023 | P0-10–13 | T08/T12/T22 |
| R07 Adoption | FR-025–030 | P0-15–17 | T13/T17/T21 |
| R08 Warnings | FR-012–013 | P0-08 | T06 |
| R09 Policies | FR-021–024, FR-029 | P0-13/P0-21 | T12/T14 |
| R10 Provenance | FR-004/006/019/024/032 | P0-14/P0-22 | T15 |
| R11 Failure | FR-010/016/019/020/031 | P0-18 | T09/T10/T11/T16 |
| R12 Reliability | FR-007/030–034 | P0-17/P0-19/P0-20 | T17–T18 |

## 20. Open product decisions

The following remain intentionally unresolved and retain the defaults from Document 01:

| Open ID | Decision | Default |
|---|---|---|
| O01 | Organizer permission for pre-event code/templates | Do not assume permission; confirm before implementation |
| O02 | Names assigned to roles A–D | Use role letters until team assigns owners |
| O03 | Exact supported Python/Node/component versions | Select after a clean dependency compatibility trial |
| O04 | Plain CSS or familiar styling setup | Plain CSS if the team has no established setup |
| O05 | Licensed online basemap | Blank/local geometry fallback is sufficient for P0 |

Any answer that changes P0 behavior must be recorded in Document 01’s decision log and reflected here.

## 21. PRD approval and handoff

This PRD is ready for team review when:

- every P0 capability in Document 01 maps to at least one FR;
- every FR has observable acceptance criteria;
- no requirement implies real booking, live inventory or guaranteed policy eligibility;
- the hero numbers agree with the audited dossier;
- open decisions have owners/defaults;
- the team agrees that Documents 03–07 can define implementation detail without adding product scope.

After approval, create the next document: **03 — Domain Model and India Travel Glossary**. That document must define the records, state vocabulary and invariants used here before the fixture, algorithm, architecture and API documents are written.

### Sign-off

| Role | Name | Approval | Date |
|---|---|---|---|
| Product/UI (C) |  | Pending |  |
| Domain/impact (A) |  | Pending |  |
| Planner/finance (B) |  | Pending |  |
| API/integration (D) |  | Pending |  |
