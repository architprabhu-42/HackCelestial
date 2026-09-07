# ResiliTrip — Product Decision and Scope Lock

**Document:** 01 of the ResiliTrip implementation pack  
**Version:** 1.0  
**Date:** 6 September 2026  
**Decision status:** Proposed for team sign-off  
**Applies to:** HackCelestial 3.0 PS2 prototype  
**Normative source:** `PS2_Travel_Disruption_Recovery_Dossier.md`, Revision 2

## 1. Purpose of this document

This document freezes the product that the four-person team will build. It defines the user, problem, scenario, required capabilities, limits, success conditions and rules for approving changes. The PRD, domain model, fixture specification, algorithm design, architecture, API contract, UX specification and backlog must follow these decisions.

If another document conflicts with this scope lock, this document wins until the team records and approves a change. Research evidence and corrected calculations remain in the audited dossier; this document turns them into concise product decisions.

## 2. Product decision

The team will build **ResiliTrip**, an India-first travel disruption recovery decision-support prototype.

ResiliTrip accepts a traveler’s connected itinerary, current location and constraints. When a transport service is delayed or cancelled, it calculates the effect on downstream transfers, hotel check-in and a time-sensitive commitment. It then generates feasible alternatives from a bounded service catalog, explains why each plan passes or fails, and lets the traveler adopt one as their proposed itinerary.

The product’s promise is:

> Given where I am, what I must reach and how much I can spend, show which parts of my trip fail and which recovery options still satisfy my constraints.

The HackCelestial prototype is a simulation. It does not execute bookings, cancellations, refunds or payments. All demo inventory, schedules, fares, capacities and booking policies are visibly marked as synthetic.

## 3. Problem statement fit

The [official PS2 brief](https://www.tech.alegria.co.in/tracks) requires a connected itinerary, direct and downstream impact analysis, feasible recovery plans, comparison across trade-offs, itinerary updates and proactive warnings. The locked product covers those requirements through one deep scenario rather than shallow nationwide coverage.

The [official rules](https://www.tech.alegria.co.in/rules) explicitly allow a working simulation. The team must still confirm whether any pre-event code or templates are permitted before implementation because the rules also require original development during the hackathon.

## 4. Target user and job

### Primary user

An adult independent traveler in India who has booked different parts of a journey separately and must reach a time-sensitive commitment.

The initial user is represented by **Asha**, traveling from Mumbai to Goa for a wedding. Asha has a train, local transfers, hotel check-in and a wedding arrival deadline. Before boarding, the train is delayed by three hours.

### User job

When a journey leg is disrupted, the traveler needs to understand:

- where they can physically travel from now;
- which later bookings or commitments will fail;
- which alternatives are feasible within their time and money limits;
- why a cheaper or faster option was accepted or rejected;
- which external actions still require provider confirmation.

### User assumptions for P0

- One adult traveler.
- The traveler can read and interact with an English interface.
- They provide or confirm their itinerary and current state.
- The disruption begins before the traveler boards the original train in the hero scenario.
- No accessibility constraint is active in the hero fixture, though the domain records whether accessibility facts are suitable, unsuitable or unknown.
- The traveler controls plan adoption and understands that adoption does not purchase a ticket.

Children, groups, split parties, unaccompanied minors, medical emergencies and travelers requiring guaranteed accessibility support are outside P0.

## 5. Locked scenario

The primary demo is `mumbai-goa-v2` on 26 September 2026 in `Asia/Kolkata`.

At 05:00, Asha is outside CSMT and has not boarded. Her fictional train T1 is changed from 06:00–15:30 to 09:00–18:30. She must check into a Panaji hotel before attending a wedding. The wedding begins at 19:30 and requires arrival by 19:15.

The original plan reaches the venue at 17:50 with 85 minutes of slack. After the delay, it reaches at 20:50 with negative 95 minutes of slack. The delayed train plan therefore fails the wedding constraint even though hotel check-in remains possible.

The bounded recovery catalog contains three fictional flights:

| Plan input | Cash still required | Venue arrival | Event slack | Expected result |
|---|---:|---|---:|---|
| F2 through GOX | ₹9,700 | 13:35 | +340 min | Feasible and fastest |
| F3 through GOI | ₹6,500 | 17:20 | +115 min | Feasible and cheapest |
| F4 through GOX | ₹5,700 | 20:05 | −50 min | Rejected by hard deadline |
| Wait for delayed T1 | ₹1,300 | 20:50 | −95 min | Rejected by hard deadline |

The cash budget is ₹10,000 and the maximum incremental cost is ₹9,000. The frozen original remaining spend is ₹1,300. Unconfirmed rail refund is unknown and contributes ₹0 to money available now.

These values are acceptance fixtures. A change to them requires updating the fixture specification, expected results and relevant tests together.

## 6. Locked product principles

### D01 — Feasibility before ranking

A plan must pass every hard constraint before it can be recommended. A low price or short duration cannot compensate for a missed hard deadline, wrong origin, unavailable service, insufficient capacity or exceeded budget.

### D02 — Current physical state controls recovery

The engine starts from the traveler’s known location, time and boarding state. Completed and in-progress travel cannot be rewritten. An onboard traveler can recover only from a modeled future alighting point. The system must never teleport a traveler back to Mumbai because a flight option exists there.

### D03 — Fixed services remain fixed

A flight, train or bus moves only when an event for that service changes its schedule. If the traveler reaches it late, it becomes a missed connection. The service does not wait or move to fit the traveler.

### D04 — One constraint evaluator

The impact engine, alternative planner and plan-adoption endpoint must use the same validation rules. The frontend displays results from the backend and does not independently recalculate authoritative time, cost or feasibility.

### D05 — Generated alternatives

Recovery plans must be assembled from atomic services and transfers. Finished recommendation cards cannot be hardcoded. It is acceptable to return only one or two feasible plans when the catalog contains no third valid choice.

### D06 — Explain every decision

Each plan exposes arrival, slack, cash required, incremental cost, changed bookings, source labels and failed constraints. The user can inspect why an option such as F4 was rejected.

### D07 — Honest simulation

Every demo screen displays `SYNTHETIC SCENARIO — NOT BOOKABLE`. Animation represents the scenario clock and selected route. It is not described as live vehicle tracking.

### D08 — Adoption is internal

Selecting a plan changes the proposed itinerary stored by ResiliTrip. It does not change an airline, railway, cab or hotel booking. The adoption response and UI must state that no external booking was executed.

### D09 — Unknown is not feasible

If a required capacity, time, fee, location or accessibility fact is missing, the product returns `unknown` or `needs_input`. It cannot certify the plan as feasible by substituting zero or a favorable assumption.

### D10 — Cash and refund remain separate

Cash required now is evaluated without unreceived refunds. Already-paid costs are shown separately. Potential refund, compensation and provider assistance are separate fields and cannot be used interchangeably.

### D11 — Policy uncertainty remains visible

P0 may calculate only fictional scenario policies. Official IRCTC, Indian Railways or DGCA material appears as informational verification guidance. The product does not promise legal eligibility or a rupee refund amount.

### D12 — Bounded search claims

The result describes the configured catalog, time horizon and search status. “No feasible plan in the evaluated catalog” is valid. “No route exists” or “globally optimal across India” is not.

### D13 — Reliability outranks visual scope

The graph, table, plan comparison and offline scenario must work before additional integrations, AI features or presentation effects are added. A map failure cannot prevent the user from understanding the trip.

## 7. P0: required hackathon product

Everything in this table is required for the final prototype unless the change process records a narrower fallback.

| P0 ID | Capability | Done when |
|---|---|---|
| P0-01 | Load hero fixture | Original itinerary, catalog, constraints, policies and provenance load as a valid versioned trip |
| P0-02 | Manual structured input | User can enter one small itinerary and receives field-level validation errors |
| P0-03 | Current state | Current time, typed location and not-started/onboard/completed state influence recovery |
| P0-04 | Connected itinerary | Graph and accessible table show transport, transfers, hotel and wedding dependencies |
| P0-05 | Delay replay | Three-hour T1 update changes effective times once and records its synthetic source |
| P0-06 | Cancellation replay | A service becomes unavailable and cannot be traversed |
| P0-07 | Impact calculation | Baseline and disrupted arrival/slack match the locked fixture |
| P0-08 | Risk warning | Slack below 30 minutes and at least zero is at risk; negative hard slack is infeasible |
| P0-09 | Alternative generation | Planner builds candidates from atomic flights/transfers and returns F2/F3 for the hero |
| P0-10 | Hard validation | Wait and F4 remain visible as rejected options with exact reasons |
| P0-11 | Ranking presets | Fastest selects F2, cheapest selects F3, with deterministic tie-breaking |
| P0-12 | Budget interaction | ₹7,000 leaves F3; ₹5,000 produces no feasible catalog plan |
| P0-13 | Money breakdown | F3 shows ₹6,500 cash required and ₹5,200 above original remaining spend |
| P0-14 | Provenance | Synthetic, user-reported and estimated fields remain visibly distinct |
| P0-15 | Plan adoption | F3 can be adopted against the current version and explicitly reports no external booking |
| P0-16 | Stale protection | Changing constraints or events prevents adoption of an old plan |
| P0-17 | Reset | Reset restores fixture content under a new version and invalidates previous plans |
| P0-18 | Failure states | No solution, missing facts, stale state, validation failure and infrastructure failure are distinguishable |
| P0-19 | Demo visualization | Map preview, timeline/replay, dependency graph and plan cards use the same snapshot |
| P0-20 | Offline core | Fixture, planner, graph, table, local route geometry and reset work without external APIs or map tiles |
| P0-21 | Provider handoff | Adoption view lists steps to verify availability and policy with official/provider services |
| P0-22 | Evidence labels | No screen calls synthetic inventory live, verified, available or booked |

## 8. P1: approved stretch pool

P1 features may begin only after all applicable P0 acceptance tests pass and the team has recorded a stable demo video.

| Priority | Feature | Entry condition |
|---|---|---|
| P1-01 | Minimum cash-budget relaxation | No-solution flow and unchanged-constraint rerun are tested |
| P1-02 | Second India corridor fixture | Hero scenario remains deterministic and regression-tested |
| P1-03 | Richer ticket/file import | Manual input is complete; upload deletion and confirmation behavior are defined |
| P1-04 | Hindi or Marathi explanation templates | English deterministic explanations are stable; team can review translation accuracy |
| P1-05 | Duration uncertainty ranges | Deterministic slack boundaries pass; UI can explain best/worst cases without probabilities |
| P1-06 | Next-stop onboard recovery | A specific service provides modeled stops, timing and permitted transitions |
| P1-07 | Accessibility-aware filtering | Required provider facts are known or honestly marked unknown |
| P1-08 | Authorized external status adapter | Credentials, permission, rate limits, coverage, freshness and fallback are verified before the hackathon |
| P1-09 | Natural-language itinerary parser | Structured form works; parsed fields require review and schema validation |
| P1-10 | LLM explanation paraphrasing | Deterministic explanation remains available and facts cannot be changed by the model |

P1 is a pool, not a commitment to implement all listed features.

## 9. Explicit exclusions

The following are outside the HackCelestial build:

- Real airline, railway, bus, cab, hotel or activity booking.
- Payment collection, stored cards or payment gateways.
- Actual cancellation, refund, TDR or compensation submission.
- Guaranteed availability, fares, arrival predictions or refund eligibility.
- Scraping NTES, IRCTC, airline, OTA or bus websites.
- Storing real PNRs, Aadhaar, passports, emails or payment details.
- Nationwide route completeness or global optimality.
- Production multi-user accounts and personal trip storage.
- Group travel, split parties, seat allocation or dependent travelers.
- Emergency, medical evacuation or safety-critical recommendations.
- Automated calls, messages or supplier negotiation.
- Probabilistic statements such as “42% chance of missing.”
- Airline operations optimization for aircraft, crew, gates or slots.
- A marketplace or provider dashboard.
- A chatbot as the main interface or decision engine.

An excluded feature cannot be added merely because a library or API makes a partial demo easy. It must pass the change-control process.

## 10. Data and claim boundary

| Data class | P0 source | Required UI wording | Prohibited implication |
|---|---|---|---|
| Itinerary | Fixture or user-reported | `Synthetic` or `User reported` | Provider verified |
| Disruption | Replay event | `Simulated disruption` | Live NTES/airline alert |
| Alternative service | Fixture catalog | `Synthetic option` | Currently operating/bookable |
| Fare | Fixture catalog | `Synthetic fare` | Current quotation |
| Capacity | Fixture catalog | `Synthetic seats` | Reserved or guaranteed seat |
| Transfer duration | Fixture estimate | `Scenario estimate` | Live traffic prediction |
| Policy | Fictional booking term | `Scenario policy` | Current statutory entitlement |
| External rule link | Official information source | `Verify with provider` | Legal decision or approved refund |
| Route animation | Local geometry and replay clock | `Route preview` | Live GPS tracking |

The interface must keep these labels visible in the journey and comparison views. A footnote buried only in the opening screen is insufficient.

## 11. Success criteria

### Product success

The prototype succeeds when an unfamiliar user can see the disruption, identify the affected wedding, compare the two feasible plans, understand why F4 fails, change the budget and adopt F3 without believing a ticket was purchased.

### Functional success gates

- The locked arithmetic is reproduced exactly.
- All P0 capabilities required for the chosen demo path work from real backend responses.
- Alternatives are generated from atomic catalog records.
- Every returned plan passes the shared hard-constraint evaluator.
- Duplicate events do not apply twice.
- Stale plans cannot be adopted.
- Network loss does not break the core demo.
- Reset returns the scenario to a known state.

### Performance targets

- Impact calculation and bounded search: p95 below one second over 100 warmed fixture runs on the demo laptop.
- Visible local UI response: below two seconds for the scripted demo interactions.
- These are targets until measured and recorded; they must not be presented as achieved results beforehand.

### Comprehension check

After implementation, test at least five people unfamiliar with the project. Each should answer:

1. Which feasible plan is cheapest?
2. Why is F4 rejected even though it costs less?
3. Did selecting F3 purchase a ticket?

Record answers, time and confusion. The goal is five correct answers to all three questions before the final presentation. If people confuse adoption with booking, change the UI and wording before adding stretch features.

## 12. Definition of done for the hackathon

P0 is done only when:

- the repository installs from a clean checkout using documented versions;
- the hero fixture and required tests pass on the demo laptop;
- frontend values match backend response fields;
- the graph, table and plan cards show a consistent snapshot;
- delay, budget change, rejection explanation, adoption and reset work repeatedly;
- offline mode works without external provider APIs or downloaded public OSM tiles;
- synthetic and not-bookable labels remain visible;
- third-party licenses and map attribution are present;
- another teammate can run the demo from the runbook;
- the team records a complete backup video before starting P1 work.

A polished screen with hardcoded recommendation cards does not satisfy the definition of done.

## 13. Demo story lock

The primary two-to-three-minute demonstration follows this order:

1. Load Asha’s baseline and show the 85-minute wedding buffer.
2. Replay T1’s three-hour schedule change.
3. Show the wedding at negative 95 minutes while hotel check-in remains within its window.
4. Generate F2 and F3 from the atomic catalog.
5. Inspect the rejected F4 explanation: venue arrival is 50 minutes after the hard cutoff.
6. Lower the cash limit to ₹7,000 so F2 disappears and F3 remains.
7. Adopt F3 as the proposed itinerary and show that external booking remains incomplete.
8. Preview the changed route and display the provider-verification checklist.

The backup demonstration lowers cash to ₹5,000 and shows “No feasible plan in the evaluated catalog.”

Do not replace this sequence during the last six hours unless the original path is broken and the change is recorded. The demo must show at least one live constraint change so judges can see calculation rather than a pre-scripted slideshow.

## 14. Team ownership and decision rights

Temporary role labels are used until names are assigned.

| Role | Primary authority | Required reviewer |
|---|---|---|
| A — Domain/impact | Time, graph and constraint semantics | B |
| B — Planner/finance | Candidate generation, cost and ranking | A |
| C — Product/UI | Interaction, accessibility and visual consistency | D |
| D — API/integration | Versioning, persistence, packaging and demo operation | A or B for domain effects |

No single person may approve a change to hard constraints, fixture arithmetic, financial semantics or adoption behavior. A and B must review those changes together.

## 15. Change-control rule

This document begins as **Proposed**. It becomes **Locked** when all four team members approve it. After locking, a scope change requires a decision-log entry with:

- change ID and date;
- requester and reason;
- affected P0/P1/exclusion IDs;
- effect on scenario, algorithm, API, UX, tests and demo;
- estimated work and feature removed to fund it;
- risk and rollback;
- approval from the product/UI owner and affected technical owner;
- A+B approval for time, money or feasibility changes.

Every added feature must identify an equal or larger item to remove unless P0 is already complete and recorded. Silent changes in code do not change the scope.

### Decision log

| Change ID | Date | Decision | Affected IDs | Removed/replaced work | Approvers |
|---|---|---|---|---|---|
| DL-001 | 2026-09-06 | Initial proposed scope created from audited dossier Revision 2 | All | None | Pending team sign-off |

## 16. Stop rules during the 24-hour build

- By hour 2: contracts and fixture arithmetic must be agreed. Otherwise stop UI implementation and resolve them.
- By hour 6: baseline, delay and boundary calculations must work headlessly. Otherwise keep the map static.
- By hour 9: planner must generate F2/F3 and reject F4/wait. Otherwise stop presentation polish and fix generation.
- By hour 15: adoption, stale-plan rejection and reset must work. Otherwise remove persistence complexity while keeping safe version checks.
- By hour 18: record a working demo before starting any P1 item.
- From hour 21: fix defects only.

Truth labels, current-location validation, hard deadlines, cash checks and stale-plan rejection cannot be cut to preserve an animation or extra screen.

## 17. Open decisions before coding

These items do not block drafting the PRD, but they must be resolved before implementation starts:

| ID | Decision needed | Owner | Deadline | Default if unresolved |
|---|---|---|---|---|
| O01 | Confirm allowed pre-event code/templates with organizers | Team lead | Before repository implementation | Build only after permitted start; retain design documents |
| O02 | Assign names to roles A–D | Team lead | Before backlog assignment | Temporary role letters remain |
| O03 | Confirm exact demo laptop and supported Python/Node versions after clean dependency trial | D | Architecture/implementation kickoff | No invented version claim |
| O04 | Select plain CSS versus the team’s already-familiar styling setup | C | UX specification | Plain CSS |
| O05 | Select a licensed online basemap or use only the blank/local fallback | C/D | Before map implementation | Blank background with local illustrative geometry |

The conflicted submission deadline shown across official event pages should also be confirmed immediately, but it does not change the product scope.

## 18. Sign-off

Signing means the team agrees to build P0 before P1, preserve the simulation boundary and use the change process for later additions.

| Team role | Name | Approval | Date |
|---|---|---|---|
| A — Domain/impact |  | Pending |  |
| B — Planner/finance |  | Pending |  |
| C — Product/UI |  | Pending |  |
| D — API/integration |  | Pending |  |

After approval, change `Decision status` at the top from `Proposed for team sign-off` to `Locked` and record the commit or document version in DL-001.
