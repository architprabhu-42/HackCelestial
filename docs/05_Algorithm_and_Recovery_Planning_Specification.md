# ResiliTrip — Algorithm and Recovery Planning Specification

**Document:** 05 of the ResiliTrip implementation pack  
**Version:** 1.0  
**Date:** 6 September 2026  
**Status:** Retained current-demo algorithm reference
**Future authority:** `IMPLEMENTATION_PLAN.md`; roadmap work may replace this
bounded synthetic-catalog approach through versioned implementation slices.
**Feeds:** API Contracts and test strategy

## 1. Purpose

This document defines how ResiliTrip applies disruptions, recalculates itinerary impact, generates recovery paths, evaluates constraints, handles unknown facts, computes financial totals, filters alternatives, ranks plans and revalidates adoption.

The algorithm must produce the outputs in Document 04 from its atomic service and transfer records. Returning prewritten F2/F3 recommendation objects does not satisfy this specification.

P0 uses deterministic rules and bounded exhaustive search. It does not use prediction, machine learning, an LLM, CP-SAT or external routing. These can be evaluated later without changing the P0 contract.

## 2. Algorithm goals

| Goal ID | Goal | Observable evidence |
|---|---|---|
| ALG-G01 | Physical validity | Every candidate begins from CurrentState and remains location-continuous |
| ALG-G02 | Temporal validity | Fixed cutoffs, processing time, windows and hard deadlines are enforced exactly |
| ALG-G03 | Financial validity | Cash and incremental cost reconcile from unique MoneyItems |
| ALG-G04 | Shared reasoning | Impact, candidate evaluation and adoption use the same atomic checks |
| ALG-G05 | Determinism | Same versions, time, constraints and preset produce the same outputs/order |
| ALG-G06 | Inspectability | Each pass/fail/unknown result includes structured evidence and reason code |
| ALG-G07 | Bounded completeness | Complete/no-plan claims apply only to the configured catalog, horizon and leg limits |
| ALG-G08 | Safe uncertainty | Required unknown facts never become favorable defaults |
| ALG-G09 | Retry safety | Duplicate events cannot compound delays or create new versions |
| ALG-G10 | Demo speed | Small fixture is evaluated without an optimization service or network dependency |

## 3. Inputs and outputs

### 3.1 Impact evaluation input

- immutable TripSnapshot;
- immutable CatalogSnapshot;
- current replay instant;
- active itinerary activities/dependencies;
- accepted effective service state;
- Constraints and field-level Provenance.

### 3.2 Planner input

`PlannerRequest` contains:

- `trip_id` and `expected_trip_version`;
- `catalog_version`;
- ranking preset;
- current replay instant;
- search limits from the locked scenario.

The server loads authoritative trip/catalog data. Client-submitted prices, capacity, totals, statuses or generated plan objects are ignored or rejected.

### 3.3 Planner output

`PlannerResult` contains:

| Field | Meaning |
|---|---|
| Result status | `complete`, `no_feasible_catalog_plan`, `needs_input`, `partial_search`, or `error` |
| Search scope | Catalog version, horizon, service/activity/leg bounds and replay instant |
| Search completeness | Boolean plus interruption reason when false |
| Feasible plans | Certified hard-valid plans after frontier filtering and preset ordering |
| Uncertain plans | Complete physical paths with one or more required null checks |
| Rejected plans | Complete paths with known hard failures; display may summarize beyond a small set |
| Counts | States expanded, complete paths, duplicates, feasible/unknown/rejected and prune reasons |
| Runtime | Monotonic elapsed milliseconds for measurement only |

The primary comparison shows at most three feasible frontier plans. Result data may retain more rejected summaries for explanation.

## 4. One shared constraint library

The implementation must expose pure domain functions used by the impact engine, planner and adoption validator. Each function returns a `ConstraintCheck`; it must not mutate trip or catalog state.

| Function | Inputs | Result |
|---|---|---|
| `check_current_state` | current state, replay instant | Valid start or reason/needs-input |
| `check_location_continuity` | prior location, next origin | Pass or `LOCATION_UNREACHABLE` |
| `check_service_status` | service | Pass or `SERVICE_CANCELLED` |
| `check_service_readiness` | ready time, effective departure, origin allowance | Slack/check or `SERVICE_CUTOFF_MISSED` |
| `check_capacity` | known capacity, party size | Pass, `CAPACITY_INSUFFICIENT`, or null/`CAPACITY_UNKNOWN` |
| `check_accessibility` | option value, requirement | Pass, fail, or null |
| `schedule_transfer` | ready time, template | Scheduled instance or window/capacity failure |
| `schedule_processing` | ready time, duration | Scheduled processing or input failure |
| `schedule_hotel` | ready time, window, duration | Scheduled hotel activity or `ACTIVITY_WINDOW_MISSED` |
| `check_commitment` | ready time, event start, readiness allowance | Slack/status or `HARD_DEADLINE_MISSED` |
| `check_search_bounds` | label, horizon/leg limits | Pass or `SEARCH_HORIZON_EXCEEDED`, `MAX_FIXED_LEGS_EXCEEDED`, or `MAX_TRANSFER_LEGS_EXCEEDED` |
| `build_money_items` | selected path, original bookings, policies | Unique items plus unknown fee flags |
| `check_finance` | money items, baseline, limits | Cash/increment checks |
| `summarize_plan_status` | complete check list | feasible/at-risk/infeasible/unknown |

Each check records:

- stable constraint ID;
- true, false or null result;
- reason code;
- observed value;
- required value;
- relevant provenance IDs.

Failing fast is allowed during search pruning, but full candidate evaluation must return all independently evaluable failures needed for explanation.

## 5. Validation before algorithms run

### 5.1 Structural validation order

1. Parse strict types; reject unknown fields where the API schema forbids them.
2. Validate unique IDs and referenced records.
3. Validate timezone-aware chronology and numeric ranges.
4. Validate activity-specific required/forbidden fields.
5. Validate the dependency DAG.
6. Validate CurrentState phase invariants.
7. Validate P0 bounds and simulation flags.
8. Validate financial item uniqueness and baseline reconciliation.

Structural failure returns validation errors and does not invoke impact/search.

### 5.2 Required unknowns

Some fields are nullable by design. Null is allowed structurally when the domain supports unknown, but the corresponding constraint becomes null during evaluation. For example, `capacity=null` is valid data and produces `CAPACITY_UNKNOWN` when capacity is required.

### 5.3 Stable ordering

Before traversal, sort:

- dependency successors by activity ID;
- services by effective departure then service ID;
- transfers by earliest start then transfer ID;
- constraint results by a fixed reason-priority list then constraint ID.

Do not rely on database row order, map iteration order or frontend sorting.

## 6. Event application algorithm

### 6.1 Transactional sequence

```text
apply_event(trip_id, request):
  begin transaction
  trip = load current trip snapshot

  prior = find event by (trip_id, event_id)
  if prior exists:
      if canonical_payload(prior) == canonical_payload(request):
          return DUPLICATE_EVENT with applied=false and current snapshot
      return EVENT_ID_CONFLICT

  if request.expected_trip_version != trip.version:
      return VERSION_CONFLICT

  if request.source_sequence <= latest_sequence(trip_id, request.source_id):
      return EVENT_SEQUENCE_STALE

  validate supported event union and service reference
  next = copy trip snapshot

  if SERVICE_TIMING_UPDATED:
      require new departure and new arrival
      require new arrival > new departure
      replace service effective departure and arrival in next
      set status = delayed when effective differs from scheduled else scheduled

  if SERVICE_CANCELLED:
      set service status = cancelled

  next.version = trip.version + 1
  impacts = evaluate_itinerary(next, catalog)
  append immutable event and next snapshot
  mark older preview plans stale
  commit
  return applied=true, next snapshot, impacts
```

Canonical payload excludes transport-level request metadata but includes every domain field. The API document will define the exact canonicalization. Duplicate detection occurs before expected-version comparison so a safe retry of an already-applied request returns duplicate rather than a misleading version conflict.

### 6.2 Event rules

- Timing events use absolute replacement times.
- Updating T1 to 09:00–18:30 twice leaves it at 09:00–18:30.
- Cancellation is service unavailability, not a numeric delay.
- Unsupported weather/gate events fail validation and do not mutate state.
- P0 has one authoritative replay source; source-conflict arbitration is out of scope.
- Recomputing the entire active itinerary is required after mutation. With at most 20 activities, incremental caching adds correctness risk without meaningful benefit.

## 7. Itinerary impact evaluation

### 7.1 Evaluation outputs

`evaluate_itinerary` returns scheduled activity instances, ConstraintChecks, Impact records and overall status. It operates on a complete selected itinerary, not the alternative catalog.

### 7.2 Starting readiness

For an itinerary being evaluated from now:

```text
initial_ready_time = current_state.as_of + decision_allowance
initial_location = current_state.location_id
```

The original baseline may also be evaluated from its stored planned start for before/after comparison. The call must explicitly name `evaluation_mode=baseline` or `evaluation_mode=current`; no hidden choice based on whether an event exists.

Completed activities retain recorded actual/effective times and locations. An active onboard service is frozen through its supported recovery point. If that point is absent, current recovery evaluation returns `needs_input` before it constructs candidates.

### 7.3 Activity scheduling rules

Process the dependency DAG in stable topological order.

For each activity, compute required predecessor readiness. If a required physical predecessor is blocked, mark this activity blocked and preserve the causal reason.

#### Fixed transport

1. Confirm prior location equals service origin.
2. Confirm service is not cancelled.
3. Confirm capacity/accessibility/mode facts.
4. Calculate boarding cutoff = effective departure − origin allowance.
5. If ready time is after cutoff, fail `SERVICE_CUTOFF_MISSED`; the activity and physical descendants are blocked.
6. Otherwise allow idle waiting; activity start/end equal effective service times.
7. Set location to service destination.
8. Materialize the service’s exit allowance once as a processing activity when the itinerary contains/requires it.

#### Flexible transfer

1. Confirm current location equals template origin.
2. Confirm capacity/accessibility/mode facts.
3. Start at `max(ready_time, window_start)`.
4. If start is after `latest_start`, fail `ACTIVITY_WINDOW_MISSED`.
5. End at start + positive duration; set location to destination.

#### Processing

Start at readiness, end after its positive duration, remain at the same location.

#### Hotel check-in

1. Require the hotel location.
2. Start at `max(ready_time, earliest_start)`.
3. Start at or before `latest_start` passes; later fails.
4. End after check-in duration.

#### Commitment

1. Require readiness at the commitment location.
2. Cutoff = event start − readiness allowance.
3. Slack = cutoff − ready time in exact seconds.
4. Negative hard slack fails; zero through threshold minus one second is at risk; threshold or more is feasible under current facts.
5. The commitment itself does not move.

### 7.4 Overall status

```text
if any required ConstraintCheck is false:
    overall = infeasible or blocked according to physical cause
else if any required ConstraintCheck is null:
    overall = unknown
else if any relevant slack is >= 0 and < risk_threshold:
    overall = at_risk
else:
    overall = feasible
```

Known failure takes precedence over unknown for the overall candidate, while both checks remain visible. A candidate that misses the wedding and also has unknown accessibility is rejected for the known deadline; it is not promoted to merely unknown.

### 7.5 Impact diff

To explain an event:

1. evaluate the prior snapshot;
2. evaluate the new snapshot;
3. compare activity start/end/status/slack;
4. create Impact only for changed or causally blocked activities;
5. attach the root event and the shortest dependency path from its service activity to the affected activity;
6. preserve both before/after values.

If several equally short causal paths exist, choose the lexicographically smallest activity-ID sequence for deterministic display. P0 does not compute probabilistic causality.

## 8. Recovery frontier and required obligations

### 8.1 Freeze the past

Derive a recovery frontier from CurrentState:

- completed activities are frozen;
- active service remains frozen until a supported recovery point;
- unstarted affected suffix can be replaced;
- unaffected original obligations after the frontier remain required unless explicitly optional and omitted by user consent.

For the hero, the frontier is CSMT at 05:00 before boarding. Decision-ready time is 05:15. Required ordered obligations are H1 at the hotel and E1 at the venue.

### 8.2 Obligation order

P0 derives an ordered list from the original itinerary. Each obligation includes location, window/cutoff, duration and hard flag. The hero order is:

```text
H1 hotel check-in → E1 wedding commitment
```

Search cannot skip H1 to reach E1 because both are hard in this scenario. Supporting alternative order, parallel obligations or explicit optional omissions is future work.

## 9. Search graph and label

### 9.1 Indexes

Build immutable indexes:

- `services_by_origin[location_id]`, sorted by effective departure and ID;
- `transfers_by_origin[location_id]`, sorted by window start and ID;
- `required_obligations`, ordered;
- booking/policy lookup by ID.

### 9.2 SearchLabel

| Field | Meaning |
|---|---|
| `location_id` | Current physical location |
| `ready_time` | Earliest next action time |
| `next_obligation_index` | First required obligation not yet completed |
| `steps` | Ordered service/transfer/processing/obligation selections |
| `used_service_ids` | Prevent repeat service use |
| `used_transfer_ids` | Prevent repeat template use in P0 |
| `new_fixed_leg_count` | Search-bound counter |
| `transfer_leg_count` | Search-bound counter |
| `money_intents` | Candidate selections used for final finance calculation |
| `changed_original_booking_ids` | Original bookings whose intended action changes |
| `constraint_checks` | Early checks and prune reasons |
| `earliest_valid_until` | Earliest exclusive action/source cutoff in the selected path |

Time strictly increases for every materialized action. Idle waiting before a fixed service is implicit and does not count as a transfer/activity.

## 10. Bounded exhaustive candidate enumeration

### 10.1 Why this method

The fixture has four fixed services and five transfers. Bounded depth-first enumeration is easier to inspect and test than an optimizer. It can prove completeness within the declared small catalog and limits when the stack is exhausted.

### 10.2 Expansion order

At a label:

1. If current location matches the next hard obligation, attempt that obligation first. A hard obligation at the current location cannot be bypassed by an outgoing transfer.
2. If all obligations are complete, finalize the candidate.
3. Otherwise expand valid fixed services from the location in stable order.
4. Expand valid transfer templates from the location in stable order.

This produces deterministic traversal. Final plan ordering still comes from ranking, not discovery order.

### 10.3 Pseudocode

```text
enumerate_candidates(trip, catalog, request):
  start = build_frontier(trip.current_state)
  if start is unknown/unsupported:
      return needs_input

  initial = SearchLabel(
      location=start.location,
      ready_time=start.time + decision_allowance,
      next_obligation_index=0,
      steps=frozen_prefix,
      earliest_valid_until=null
  )

  stack = [initial]
  completed = []
  rejected_partial_counts = Counter()
  deadline = monotonic_now() + runtime_guard

  while stack not empty:
      if monotonic_now() >= deadline:
          return partial_search(completed, rejected_partial_counts)

      label = stack.pop()
      count state_expanded

      bound = check_search_bounds(label)
      if bound fails:
          count bound reason
          continue

      obligation = required_obligations[label.next_obligation_index]
                   if any remain else null

      if obligation != null and label.location == obligation.location:
          result = schedule_or_check_obligation(label, obligation)
          if result passes:
              push copy with obligation step, updated time/index/checks
          else:
              record rejected candidate/partial reason
          continue

      if obligation == null:
          completed.append(finalize_and_evaluate(label))
          continue

      successors = []

      for service in services_by_origin[label.location]:
          if service.id already used: continue
          transition = try_service(label, service)
          if transition passes/has allowed unknowns:
              successors.append(transition)
          else:
              count prune reason

      for transfer in transfers_by_origin[label.location]:
          if transfer.id already used: continue
          transition = try_transfer(label, transfer)
          if transition passes/has allowed unknowns:
              successors.append(transition)
          else:
              count prune reason

      push successors in reverse stable order so the first stable item is popped first

  evaluated = evaluate_full_candidates(completed)
  return classify_deduplicate_frontier_rank(evaluated, request.preset)
```

Unknown transitions may remain in exploration so the product can explain an uncertain complete option. They never enter certified feasible plans.

### 10.4 Service transition

`try_service` performs location, status, mode, capacity, accessibility, cutoff and bound checks. If traversable:

- append fixed-transport step with effective times;
- append one processing step for exit allowance when positive;
- advance to destination at arrival + exit;
- increment fixed-leg count when service is new relative to frozen prefix;
- set validity to the earlier of existing validity, boarding cutoff and source validity;
- record booking selection and potential changed-original-booking effect.

Taking T1 after D1 is allowed because decision-ready 05:15 is before its 08:30 readiness cutoff. It later fails the wedding, so it becomes a complete rejected candidate rather than an early service prune.

### 10.5 Transfer transition

`try_transfer` performs origin, mode, capacity, accessibility, window and bound checks. If traversable:

- start at the later of ready time/window start;
- append transfer step;
- advance to destination at start + duration;
- increment transfer count;
- set validity to the earlier of existing validity, latest start and source validity;
- record its booking/money intent.

For X1, start and latest start both equal 05:15. Flight plans therefore receive an exclusive `valid_until=05:15`, even though the transfer schedule begins at that instant. Adoption must occur before the action begins.

### 10.6 Cycles and termination

P0 prevents repeated service IDs and repeated transfer-template IDs within one path. Every action has positive duration, and fixed-service times are chronological. Semantic limits bound fixed and transfer legs and the 24-hour horizon.

The algorithm does not use aggressive dominance pruning in P0. Two labels at the same location/time can differ in completed obligations, booking changes, fees or provenance. Incorrect dominance would silently discard a valid explanation or cheaper path. The small catalog makes exhaustive bounded traversal practical.

## 11. Candidate finalization and shared evaluation

For every complete physical path:

1. Materialize a complete activity/dependency itinerary.
2. Add retained and changed booking effects.
3. Build unique MoneyItems from selected actions and fictional policies.
4. Evaluate the entire itinerary through the shared evaluator.
5. Evaluate cash and incremental-cost constraints.
6. Attach all ConstraintChecks and provenance.
7. Calculate changed original booking IDs.
8. Calculate per-plan exclusive validity cutoff.
9. Assign feasibility class.
10. Create a deterministic signature and ID.

Final evaluation must not trust early search checks alone. It catches bugs in transition construction and guarantees that impact display and recovery validation use the same semantics.

### 11.1 Candidate signature and identity

Canonical signature:

```text
trip_version | catalog_version | ordered service/transfer/obligation IDs
```

The hero fixture uses readable stable IDs `plan:F2:v2`, `plan:F3:v2`, `plan:F4:v2`, and `plan:WAIT-T1:v2`. A general implementation may add a deterministic short hash when two different sequences would receive the same readable ID. The sequence, not the label, determines equality.

### 11.2 Deduplication

Candidates are duplicates when their canonical ordered action-ID sequence is identical. Keep the lexicographically smallest plan ID and merge identical reason/provenance references. Do not deduplicate merely because arrival/cost totals match.

## 12. Financial evaluation

### 12.1 Build money items

For each selected action:

- If its original booking is retained, include only its remaining due charge once.
- If it is a new service/transfer, include its selected price as `new_purchase/due`.
- If an original booking is abandoned, apply an explicit known fictional mandatory fee, if any.
- Keep already-paid original amounts as separate sunk context.
- Keep potential refunds as null/potential unless a received refund is explicitly recorded.

After action-level items, deduplicate by MoneyItem ID. Conflicting duplicate IDs with different content invalidate the candidate.

### 12.2 Formulas

```text
cash_required = sum(amount of due retained_charge, new_purchase, mandatory_fee)

incremental_cost = cash_required - frozen_baseline_remaining_spend
```

Potential/received-refund handling follows Document 03. The hero potential train refund is null and excluded.

### 12.3 Checks

- `cash_required <= max_cash_required`
- `incremental_cost <= max_incremental_cost`

Both must pass. Equality passes. One paise over fails. No float conversion is permitted.

### 12.4 Changed-booking count

Count distinct original booking IDs whose intended original action is abandoned or replaced. Do not count each new purchase as another changed original booking.

For every flight path in the hero:

- `booking:train-original` is abandoned;
- `booking:cab-C1` is abandoned;
- H1 and C2 are retained;
- changed original booking count = 2.

Wait uses all original booking intentions, so its count is 0 even though it later fails the event.

## 13. Feasible, uncertain and rejected sets

Classify each fully evaluated candidate:

```text
if any hard check == false:
    rejected
else if any required hard check == null:
    uncertain
else:
    feasible (with at-risk label when any relevant slack is below threshold)
```

At-risk plans are feasible for hard filtering and appear in the feasible set with a warning. Unknown plans appear separately and cannot be recommended or adopted in P0.

Rejected plans are useful explanations. Keep at least:

- the lowest-cash rejected complete path;
- the fastest rejected complete path;
- any path explicitly selected by a user for “why rejected?”;
- a count by primary reason.

For multiple failures, choose primary reason by fixed priority:

1. current-state/location discontinuity;
2. cancelled/missed service;
3. hard commitment/window;
4. capacity/accessibility;
5. cash/incremental cost;
6. search bounds;
7. other validation.

All known failures remain in the detailed check list even when only one appears on the card.

## 14. Pareto frontier

### 14.1 Objective vector

For feasible candidates, minimize:

```text
(cash_required_paise, final_required_arrival_epoch, changed_original_booking_count)
```

Earlier arrival is a lower epoch value. A candidate A dominates B if A is no worse on all three objectives and strictly better on at least one.

### 14.2 Frontier procedure

```text
frontier = []
for candidate in feasible candidates sorted by plan ID:
    if any other feasible candidate dominates candidate:
        mark candidate dominated
    else:
        frontier.append(candidate)
```

The P0 catalog is small, so pairwise `O(P²)` comparison is acceptable and more transparent than a specialized structure.

F2 and F3 both remain on the hero frontier: F2 arrives earlier; F3 costs less; both change two original bookings. Neither dominates the other.

### 14.3 Display bound

Rank the full frontier, then show the first three. Return `frontier_total` and `displayed_count`. Do not discard the fact that more frontier plans existed. If the frontier has two plans, display two.

## 15. Ranking

Rank only feasible frontier plans. All tuple elements use normalized comparable types; no mixed weighted score is computed.

```text
cheapest:
  (cash_required_paise, final_arrival_epoch, changed_count, plan_id)

fastest:
  (final_arrival_epoch, cash_required_paise, changed_count, plan_id)

fewest_changes:
  (changed_count, cash_required_paise, final_arrival_epoch, plan_id)
```

For the hero:

| Preset | Result |
|---|---|
| Cheapest | F3 then F2 |
| Fastest | F2 then F3 |
| Fewest changes | F3 then F2 because both have count 2 and F3 needs less cash |

Changing the preset must never make F4 or wait eligible. “Protect event” remains a hard setting.

## 16. Search completeness and result status

### 16.1 Complete bounded search

`search_complete=true` only when:

- all input records fit declared P0 limits;
- validation succeeds;
- CurrentState is sufficient;
- the traversal stack exhausts without runtime interruption;
- every completed path is finalized/evaluated;
- no internal error occurs.

Paths pruned for the declared horizon and leg limits do not make the search partial. Those limits define the search space and must appear in the response.

### 16.2 Partial search

A runtime guard, cancellation request or unexpected expansion guard before stack exhaustion produces `partial_search` and `SEARCH_INCOMPLETE`. Available plans may be displayed as partial options but cannot be labeled globally cheapest/fastest within the declared space unless that property was separately proven. Adoption of partial-search plans is disabled in P0.

### 16.3 No feasible plan

Return `no_feasible_catalog_plan` only after a complete bounded search with zero feasible plans. Uncertain-only results also return `needs_input` with uncertain options, not no solution.

### 16.4 Runtime guard

The architecture may choose a configurable monotonic runtime guard. The value is an operational setting, not a domain cutoff. The planned performance test measures 100 warmed hero searches; it does not skip completeness checks to meet a target.

## 17. Plan validity

Each plan calculates its own exclusive `valid_until` as the minimum of:

- selected transfer latest-start/action cutoff;
- selected fixed-service boarding cutoff;
- required source/catalog validity cutoff;
- any earlier domain validity boundary.

If no future selected action has a cutoff, use the search horizon or explicit catalog validity.

Hero values:

| Plan | Exclusive valid-until | Reason |
|---|---|---|
| F2 | 05:15 | X1 exact start/latest start |
| F3 | 05:15 | X1 exact start/latest start |
| F4 | 05:15 | X1 exact start/latest start; plan is already rejected |
| Wait T1 | 08:30 | T1 effective departure 09:00 minus 30-minute readiness allowance; plan is already rejected |

At replay time equal to `valid_until`, adoption fails. Regeneration must use a new CurrentState; it cannot simply extend the timestamp.

## 18. Adoption revalidation

```text
adopt_plan(trip_id, plan_id, expected_version, acknowledge_simulation):
  require acknowledge_simulation == true
  begin transaction
  trip = load current trip
  plan = load server-owned plan

  require expected_version == trip.version
  require plan.trip_version == trip.version
  require plan.catalog_version == trip.catalog_version
  require plan.status == preview
  require replay_now < plan.valid_until
  require previous planner result was complete

  reevaluated = evaluate_full_plan(plan, trip, catalog)
  require reevaluated is feasible or at_risk
  require money and sequence signature equal stored authoritative plan

  adoption = append immutable adoption with external_booking_executed=false
  next_trip = create version + 1 with adopted proposed itinerary
  mark other previews stale
  commit
  return next_trip, adoption, provider action checklist
```

Unknown, rejected, partial-search or expired plans cannot be adopted. The server does not accept a client-modified plan to bypass checks.

## 19. Reset algorithm

Reset is a mutation, not deletion/recreation of the trip ID.

1. Require expected current version.
2. Load the immutable scenario baseline and catalog version.
3. Create a new trip version whose content matches the baseline fixture.
4. Append a reset audit record.
5. Mark all previous previews stale.
6. Preserve monotonic version history.

Repeated resets continue to increment versions. They do not make `plan:F3:v2` valid again.

## 20. Deterministic explanations

Explanations are templates over ConstraintChecks and computed fields. An optional LLM may later paraphrase the final structured explanation, but the deterministic text remains the fallback and source of truth.

### 20.1 Template inputs

- activity/service display names;
- observed and required values;
- time/currency formatting;
- reason code;
- source labels;
- plan rank reason.

### 20.2 Required templates

| Reason/result | Template content |
|---|---|
| Deadline miss | `{plan} reaches {commitment} at {arrival}, {late_by} after the {cutoff} required arrival.` |
| Cash failure | `{plan} requires {cash}; your current cash limit is {limit}.` |
| Capacity unknown | `Capacity for {service} is unknown, so this option cannot be certified.` |
| Location failure | `The traveler is at {actual}; this option starts at {required_origin} with no connecting step.` |
| At risk | `{plan} passes the deadline with {slack} remaining, below the {threshold} warning threshold.` |
| Cheapest rank | `Lowest cash required among feasible frontier plans.` |
| Fastest rank | `Earliest final required arrival among feasible frontier plans.` |
| Adoption | `Plan adopted inside ResiliTrip. No external booking was changed.` |

The UI must format negative/positive slack from exact seconds and must not invent probabilities.

## 21. Hero execution trace

### 21.1 After D1

1. Event D1 replaces T1 effective time with 09:00–18:30 and creates trip version 2.
2. Full itinerary reevaluation schedules exit 18:30–18:50, C1 18:50–20:00, H1 20:00–20:20 and C2 20:20–20:50.
3. E1 cutoff is 19:15; slack is −5,700 seconds; original plan is rejected.

### 21.2 Search expansions that matter

At CSMT 05:15, two useful successors exist:

- T1, cutoff 08:30; and
- X1, start/latest 05:15, arriving BOM T2 06:45.

T1 completes a wait path and fails E1. X1 reaches BOM, where F2/F3/F4 all pass their boarding cutoffs. Each service inserts its own 30-minute exit, uses its destination-specific hotel transfer, completes H1 and uses C2 to E1.

### 21.3 F3 computed record

```text
current state            CSMT 05:00
decision ready           CSMT 05:15
X1                       BOM T2 06:45
F3 cutoff                12:00, pass
F3                       14:00–15:15
processing               GOI 15:15–15:45
GOI→hotel                15:45–16:30
H1                       16:30–16:50
C2                       venue 17:20
E1 cutoff                19:15
slack                     6,900 sec
cash                      650,000 paise
increment                 520,000 paise
changed originals         train, C1
valid until               05:15 exclusive
status                    feasible
```

F3 joins the frontier and ranks first for cheapest. No line above is read from an expected final plan card.

## 22. Perturbation behavior

| Fixture case | Algorithm behavior |
|---|---|
| FX-01 ₹7,000 | Full search still constructs F2, but finance rejects it; F3 is sole feasible plan |
| FX-02 ₹5,000 | F2/F3 fail cash; F4/wait fail event; complete result has no feasible plan |
| FX-03 cancel F3 | Service transition rejects F3; F2 remains |
| FX-04 +100 min F3 | Recomputed venue 19:00; +900 sec; at-risk but feasible |
| FX-05 +116 min F3 | Recomputed venue 19:16; −60 sec; rejected |
| FX-06 cancel T1 | Original physical chain blocked; X1 flight branches still evaluated |
| FX-07 capacity 0 | `CAPACITY_INSUFFICIENT`; F3 rejected |
| FX-08 capacity null | F3 completes into uncertain set; F2 remains certified |
| FX-09 accessibility required | Every required road transfer is unknown; no certified plan, return needs-input |
| FX-10 clock at 05:15 | Flight previews expire; regenerate; rejected wait path is never adoptable |
| FX-11 incomplete onboard state | `check_current_state` stops search; no CSMT alternatives |
| FX-12 duplicate D1 | Duplicate disposition; no version/timing change |
| FX-13 D1 ID conflict | Conflict; no mutation |
| FX-14 stale expected version | Conflict; no mutation |
| FX-15 interrupted traversal | Partial result; no global cheapest/fastest label; adoption disabled |

## 23. P1 minimum cash relaxation

P1 may explain the smallest cash limit that admits a plan without changing other constraints.

Method:

1. Use complete evaluated candidates from the same trip/catalog version.
2. Keep candidates whose only false hard check is `CASH_LIMIT_EXCEEDED`.
3. Continue to enforce incremental cost, event, location, capacity, accessibility, mode, horizon and leg limits.
4. Select the minimum `cash_required` among that set.
5. Difference = required cash − current cash limit.
6. Present a proposed constraint change; do not alter the trip automatically.
7. User saves the new budget, creating a new version, then regenerates plans.

For ₹5,000, F3 requires ₹6,500, so the minimum increase is ₹1,500. F4’s ₹5,700 is not eligible because it also misses E1.

## 24. Complexity and performance

### 24.1 Impact

Topological evaluation is `O(V + E + C)` for activities, dependencies and checks, excluding sorting performed during validation. With P0 at 20 activities, recomputing fully is preferred.

### 24.2 Enumeration

Worst-case path enumeration is exponential in branching and depth, approximately `O(B^D)`. P0 controls this through:

- at most 50 service instances;
- at most 2 new fixed legs;
- at most 8 transfers;
- 24-hour horizon;
- no repeated service/template within a path;
- positive time progression;
- optional runtime guard with explicit partial status.

Performance success is measured on the locked fixture. The target is p95 below one second over 100 warmed runs on recorded hardware. The design does not claim acceptable nationwide scaling.

### 24.3 Memory

Depth-first traversal stores the active stack and completed candidate records. Keep full rejected details only for configured representative plans and aggregate other reason counts to avoid unnecessary growth.

## 25. Logging and diagnostics

Structured safe fields:

- trip version and catalog version;
- event disposition/reason code;
- states expanded and completed paths;
- prune counts by reason;
- feasible/uncertain/rejected/frontier counts;
- search complete flag and interruption reason;
- runtime milliseconds;
- adoption revalidation outcome.

Do not log fictional/user names by default, full arbitrary input, booking references or external URLs. Determinism debugging should rely on versions, canonical sequence signatures and reason codes.

## 26. Algorithm acceptance criteria

| ALG ID | Criterion | Evidence |
|---|---|---|
| ALG-01 | D1 is idempotent | FX-12 and event transaction test |
| ALG-02 | Fixed T1/F2/F3/F4 times move only through their own events | impact/search tests |
| ALG-03 | Hotel and transfers schedule through declared windows | baseline/D1/F2–F4 traces |
| ALG-04 | Negative one-second hard slack fails; zero passes at-risk | boundary tests |
| ALG-05 | CurrentState prevents teleportation | FX-11 and GOI/GOX mismatch test |
| ALG-06 | Complete paths come from atomic services/transfers | sequence assertions and mutation tests |
| ALG-07 | Full evaluator agrees across impact, planning and adoption | shared-function contract tests |
| ALG-08 | Unknown capacity/accessibility cannot enter feasible set | FX-08/FX-09 |
| ALG-09 | Money totals reconcile once | F2/F3/F4/Wait plus duplicate-reference test |
| ALG-10 | Cash and incremental limits apply independently | equality/one-paise-over tests |
| ALG-11 | F2/F3 frontier and all preset orders match fixture | golden ranking test |
| ALG-12 | F4/wait remain rejected under every preset | hard-before-ranking test |
| ALG-13 | Search status reflects exhaustion/interruption | complete/no-plan/partial tests |
| ALG-14 | Every Plan has its own exclusive validity cutoff | 05:15/08:30 boundary tests |
| ALG-15 | Stale/unknown/rejected/partial plans cannot be adopted | adoption tests |
| ALG-16 | Reset restores baseline content and keeps versions monotonic | reset test |
| ALG-17 | Same authoritative inputs produce byte-stable ordered domain results after canonical serialization | determinism test |
| ALG-18 | UI explanation facts can be rendered from ConstraintChecks alone | reason-template test |

### 26.1 Traceability to product requirements and fixture evidence

| Algorithm capability | PRD requirements | Algorithm criteria | Canonical evidence |
|---|---|---|---|
| Safe disruption ingestion and recomputation | FR-008–FR-010 | ALG-01–ALG-03, ALG-17 | D1; FX-06, FX-12–FX-14 |
| Dependency-aware impact and hard deadlines | FR-011–FR-013 | ALG-03–ALG-05, ALG-07 | Baseline, D1, FX-04–FX-06, FX-11 |
| Bounded alternative construction | FR-014–FR-020 | ALG-05–ALG-08, ALG-13 | F2–F4 and wait; FX-03, FX-07–FX-09, FX-15 |
| Transparent price and policy treatment | FR-021–FR-024 | ALG-09–ALG-10 | F2/F3/F4/wait reconciliations; FX-01–FX-02 |
| Frontier, ranking and explanations | FR-025–FR-027 | ALG-11–ALG-12, ALG-18 | Cheapest/fastest/fewest-changes golden outputs |
| Preview validity and safe adoption | FR-028–FR-030 | ALG-14–ALG-16 | Per-plan cutoffs; FX-10 and reset tests |
| Reliability and inspectability | FR-031–FR-034 | ALG-01, ALG-13, ALG-17–ALG-18 | Duplicate/conflict/partial/determinism tests |

If an FR identifier changes in the PRD, this table must be updated in the same change. Passing an algorithm test does not waive its linked product requirement; the API and end-to-end test documents must preserve both sides of the mapping.

## 27. Implementation module boundary

The architecture document may rename files, but these responsibilities must remain separate:

| Module responsibility | Owns | Must not own |
|---|---|---|
| Validation | Structural and cross-reference invariants | Ranking/UI copy |
| Event application | Idempotency, sequence, versioned mutation | Candidate generation |
| Constraint library | Pure atomic checks/schedulers | Database transactions |
| Impact evaluator | Full selected-itinerary scheduling and diff | Alternative catalog traversal |
| Candidate enumerator | Bounded search and path materialization | Independent feasibility formulas |
| Finance | MoneyItem creation, totals and checks | Provider refund entitlement |
| Frontier/ranking | Deduplication, dominance and tuple ordering | Hard eligibility |
| Explanation | Reason-code templates | Fact generation |
| Adoption | Version/validity recheck and trip mutation | External booking |

## 28. Decisions fixed by this specification

| Decision ID | Resolution |
|---|---|
| ALG-D01 | Recompute the full small itinerary after each mutation |
| ALG-D02 | Use bounded DFS with stable ordering and no unsafe dominance pruning during search |
| ALG-D03 | Keep unknown complete candidates separate from feasible/rejected sets |
| ALG-D04 | Compute Pareto frontier only after full hard validation |
| ALG-D05 | Use pairwise frontier comparison and lexicographic ranking |
| ALG-D06 | Calculate validity per plan, not once for the result set |
| ALG-D07 | Disable adoption for partial-search outputs in P0 |
| ALG-D08 | Detect identical event retries before expected-version conflict |
| ALG-D09 | Treat the exact action-ID sequence as plan identity |
| ALG-D10 | Use deterministic templates as the authoritative explanation layer |

## 29. Open implementation parameters

| Open ID | Owner document | Parameter |
|---|---|---|
| ALG-O01 | Technical Architecture | Runtime guard default and safe cancellation mechanism |
| ALG-O02 | API/Data Contracts | Exact serialization, canonical payload hashing and error response fields |
| ALG-O03 | Test Strategy | Property-test generators and byte-stable canonical serializer |
| ALG-O04 | UX Specification | Number and selection of representative rejected plans shown initially |
| ALG-O05 | Technical Architecture | Whether NetworkX is used only for DAG operations or also traversal helpers |

These parameters may change implementation detail without changing the algorithms’ observable behavior.

## 30. Approval

This document is ready to lock when:

- A and B independently reproduce the hero outcomes from Document 04;
- A agrees that impact and candidate evaluation share exact rules;
- B agrees that enumeration is complete within declared bounds;
- D confirms event/adoption transactions can enforce the version rules;
- C confirms all recommendation/rejection facts can be rendered from structured checks.

| Role | Name | Approval | Date |
|---|---|---|---|
| A — Domain/impact |  | Pending |  |
| B — Planner/finance |  | Pending |  |
| C — Product/UI |  | Pending |  |
| D — API/integration |  | Pending |  |

Future implementation slices must assign these algorithms to concrete modules and
transactions without duplicating or changing their rules. See
`IMPLEMENTATION_PLAN.md` and `CURRENT_DEMO_ARCHITECTURE.md` for authority.
