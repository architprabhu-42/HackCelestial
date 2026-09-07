# ResiliTrip — Reference Scenario and Fixture Specification

**Document:** 04 of the ResiliTrip implementation pack  
**Version:** 1.0  
**Date:** 6 September 2026  
**Status:** Proposed fixture baseline  
**Scenario:** `mumbai-goa-v2`  
**Depends on:** Documents 01–03  
**Feeds:** Algorithm Specification, Architecture, API Contracts, Test Strategy and demo data

## 1. Purpose

This document defines the complete deterministic scenario used to build, test and demonstrate ResiliTrip. It specifies every relevant location, service, transfer, activity, dependency, booking, financial item, policy, provenance record, disruption and expected result.

The fixture has two jobs:

1. give frontend and backend developers one shared set of facts; and
2. make every visible recommendation reproducible from arithmetic rather than a scripted card.

All schedules, fares, capacities, transfer times, policies, hotel details and venue details are fictional. Real place names and approximate coordinates provide geographic context only. The application must display:

> **SYNTHETIC SCENARIO — NOT BOOKABLE**

## 2. Fixture authority and change rule

The logical manifest in §15 is the canonical machine-readable source for this scenario until the API/Data Contract document defines its final serialized shape. Tables in this document explain the same records.

A fixture change is complete only when the team updates together:

- the manifest value;
- the explanatory table;
- all derived plan totals and timings;
- the affected acceptance cases;
- the demo script if visible behavior changes;
- the catalog version.

Changing a service time, fare, transfer duration, capacity, activity window or policy without incrementing `catalog_version` is prohibited.

## 3. Scenario narrative

Asha is traveling from Mumbai to Goa for a wedding. At 05:00 IST on 26 September 2026, she is outside CSMT and has not boarded her fictional train T1. Her original journey uses T1 to Madgaon, a cab to a Panaji hotel, hotel check-in and a cab to the wedding venue.

The wedding starts at 19:30. Asha requires 15 minutes at the venue beforehand, so her hard arrival cutoff is 19:15. Her original plan arrives at 17:50.

A synthetic update at 05:00 changes T1 from 06:00–15:30 to 09:00–18:30. The delayed original plan arrives at the wedding at 20:50. ResiliTrip evaluates waiting and three fictional Mumbai–Goa flight services. F2 and F3 pass; F4 and waiting fail the hard event cutoff.

## 4. Scenario-level constants

| Field | Value | Meaning |
|---|---|---|
| Scenario ID | `mumbai-goa-v2` | Stable fixture identity |
| Catalog version | `catalog:mumbai-goa-v2` | Immutable service/transfer/policy set |
| Schema version | `fixture-spec-1.0` | Logical manifest version |
| Mode | `demo` | Enables only fictional data and internal adoption |
| Currency | `INR` | All stored money is integer paise |
| Display timezone | `Asia/Kolkata` | All visible fixture times are IST |
| Replay start | `2026-09-26T05:00:00+05:30` | Baseline current time |
| Decision allowance | 15 min | Candidate departure cannot begin before 05:15 |
| Search horizon | 24 h | Ends at 05:00 on 27 September |
| Risk threshold | 30 min | Slack from 0 to under 30 min is at risk |
| Party size | 1 | P0 supports one adult |
| Maximum activities | 20 | Input bound |
| Maximum catalog services | 50 | Search bound |
| Maximum new fixed legs | 2 | Candidate bound; hero uses one |
| Maximum transfer legs | 8 | Candidate bound |
| Maximum displayed frontier plans | 3 | Display bound, not a required count |
| Cash limit | ₹10,000 / `1000000` paise | Hard immediate-cash constraint |
| Incremental-cost limit | ₹9,000 / `900000` paise | Hard increase over frozen remaining baseline |
| Baseline remaining spend | ₹1,300 / `130000` paise | Original C1 plus C2 due charges |

## 5. Provenance records

Provenance is attached to fields, not only whole records.

| ID | Kind | Verification | Observed/retrieved | Validity | Use |
|---|---|---|---|---|---|
| `prov:fixture:mumbai-goa-v2` | synthetic | fixture | 2026-09-06 | Scenario only | Schedules, prices, capacity, activity windows and policies |
| `prov:user:asha-state` | user_reported | fixture | 2026-09-26 05:00 IST | Until current state changes | Current location, phase and constraints |
| `prov:estimate:map-points` | estimate | fixture | 2026-09-06 | Scenario only | Approximate illustrative coordinates |
| `prov:replay:D1` | synthetic | fixture | 2026-09-26 05:00 IST | Until reset/later event | T1 timing update |
| `prov:guidance:rail-policy` | official_replay | unverified | 2026-09-06 retrieval | No asserted legal validity | Provider-verification checklist only |

`official_replay` for the policy link does not mean the information currently applies to Asha’s fictional ticket. It stores provenance for guidance, not a calculated entitlement.

## 6. Locations

Coordinates are approximate illustration inputs and must not be used to calculate fixture durations. Typed IDs control continuity.

| ID | Kind | Display name | Code/terminal | Approximate lat,lon | Source |
|---|---|---|---|---|---|
| `rail:CSMT` | rail_station | Chhatrapati Shivaji Maharaj Terminus | CSMT | 18.9398,72.8355 | estimate |
| `rail:MAO` | rail_station | Madgaon Junction | MAO | 15.2670,73.9580 | estimate |
| `airport:BOM:T2` | airport_terminal | Mumbai Airport Terminal 2 | BOM/T2 | 19.1000,72.8740 | estimate |
| `airport:GOX:ARR` | airport_terminal | Manohar International Airport Arrivals | GOX/Arrivals | 15.7443,73.8602 | estimate |
| `airport:GOI:ARR` | airport_terminal | Goa International Airport Arrivals | GOI/Arrivals | 15.3808,73.8314 | estimate |
| `place:PANAJI_HOTEL` | hotel | Asha’s fictional Panaji hotel | — | 15.4909,73.8278 | synthetic/estimate |
| `place:WEDDING_VENUE` | venue | Fictional Panaji wedding venue | — | 15.4800,73.8200 | synthetic/estimate |

GOX and GOI are distinct. A path arriving at one cannot use the other airport’s hotel transfer.

## 7. Policy records

| Policy ID | Source class | Scope | Executable P0 terms | Result outside terms |
|---|---|---|---|---|
| `policy:fictional:flex-cab:v1` | synthetic | C1, C2 and recovery road transfers | Price is due only if transfer is selected; abandoning original C1 before pickup has zero fictional fee | Unknown fees are not inferred |
| `policy:fictional:hotel-retained:v1` | synthetic | Original H1 hotel | ₹3,000 already paid; hotel retained; no additional check-in charge | Cancellation/refund not evaluated |
| `policy:fictional:new-air:v1` | synthetic | F2, F3, F4 | Listed fare becomes due if service is selected; no further fee in fixture | No real fare/refund claim |
| `policy:guidance:rail:v1` | official guidance with conflict | Original T1 booking | No executable refund amount | `needs_provider_confirmation`; potential refund null |

The policy engine must not use `policy:guidance:rail:v1` to calculate cash or incremental cost.

## 8. Service instances

All service times include the service date. `origin_allowance` is the required terminal/station readiness before departure. `exit_allowance` becomes an explicit processing activity after arrival.

| ID / display | Mode | Origin → destination | Scheduled/effective baseline | Origin allowance | Exit allowance | Capacity | Price | Status |
|---|---|---|---|---:|---:|---:|---:|---|
| `svc:T1:2026-09-26` / T1 | rail | CSMT → MAO | 06:00–15:30 | 30 min | 20 min | 1 | ₹1,800 paid | scheduled |
| `svc:F2:2026-09-26` / F2 | air | BOM T2 → GOX | 10:00–11:15 | 120 min | 30 min | 2 | ₹6,500 due if selected | scheduled |
| `svc:F3:2026-09-26` / F3 | air | BOM T2 → GOI | 14:00–15:15 | 120 min | 30 min | 2 | ₹3,800 due if selected | scheduled |
| `svc:F4:2026-09-26` / F4 | air | BOM T2 → GOX | 16:30–17:45 | 120 min | 30 min | 2 | ₹2,500 due if selected | scheduled |

The fares and seat counts are fictional. Capacity 2 is sufficient for party size 1; no seat is reserved.

## 9. Transfer templates

| ID / display | Direction | Start window | Duration | Capacity | Price | Policy |
|---|---|---|---:|---:|---:|---|
| `xfer:X1` / X1 | CSMT → BOM T2 | 05:15 exactly | 90 min | 4 | ₹1,200 | flex-cab |
| `xfer:C1` / C1 | MAO → Panaji hotel | 00:00–22:00 | 70 min | 4 | ₹800 | flex-cab |
| `xfer:C2` / C2 | Panaji hotel → wedding venue | 00:00–23:00 | 30 min | 4 | ₹500 | flex-cab |
| `xfer:X-GOX-HOTEL` | GOX → Panaji hotel | 00:00–23:00 | 60 min | 4 | ₹1,500 | flex-cab |
| `xfer:X-GOI-HOTEL` | GOI → Panaji hotel | 00:00–23:00 | 45 min | 4 | ₹1,000 | flex-cab |

Every transfer is `accessibility=unknown` because the hero does not assert an accessibility requirement. If that constraint is enabled, these options cannot be certified without updated data.

X1’s exact start makes candidate plans valid for adoption only before 05:15. It is a scenario device, not a claim that a real cab must depart at precisely that time.

## 10. Original bookings and money

### 10.1 Booking records

| Booking ID | Covers | Knowledge state | Paid | Remaining | Policy |
|---|---|---|---:|---:|---|
| `booking:train-original` | T1 | fictional | ₹1,800 | ₹0 | rail guidance, no computed refund |
| `booking:hotel-original` | H1 | fictional | ₹3,000 | ₹0 | retained hotel |
| `booking:cab-C1` | C1 | fictional | ₹0 | ₹800 | flex-cab |
| `booking:cab-C2` | C2 | fictional | ₹0 | ₹500 | flex-cab |

Flight and airport-transfer bookings are candidate-created fictional bookings. Their external state remains fictional even after internal adoption.

### 10.2 Baseline money items

| Money item ID | Category/state | Amount | Included in baseline remaining? | Included in cash now? |
|---|---|---:|---|---|
| `money:T1-paid` | sunk_cost/paid | ₹1,800 | No | No |
| `money:H1-paid` | sunk_cost/paid | ₹3,000 | No | No |
| `money:C1-due` | retained_charge/due | ₹800 | Yes | Yes for wait plan |
| `money:C2-due` | retained_charge/due | ₹500 | Yes | Yes for every hotel-to-venue path |
| `money:T1-potential-refund` | potential_refund/potential | null | No | No |

Baseline remaining spend = ₹800 + ₹500 = ₹1,300.

## 11. Original itinerary activities

The commitment activity begins at 19:30, but feasibility uses its 19:15 latest arrival cutoff.

| Activity ID | Kind/reference | Baseline start–end | Location transition/window | Hard? |
|---|---|---|---|---|
| `act:T1` | fixed_transport / T1 | 06:00–15:30 | CSMT → MAO | Yes |
| `act:T1-exit` | processing | 15:30–15:50 | At MAO, 20 min | Yes |
| `act:C1` | flexible_transfer / C1 | 15:50–17:00 | MAO → hotel | Yes |
| `act:H1` | hotel_checkin | 17:00–17:20 | Start window 12:00–21:00; 20 min | Yes in hero |
| `act:C2` | flexible_transfer / C2 | 17:20–17:50 | Hotel → venue | Yes |
| `act:E1` | commitment | Event at 19:30 | Venue; arrival required by 19:15 | Yes |

Dependencies are a single chain with zero additional buffer:

```text
act:T1 → act:T1-exit → act:C1 → act:H1 → act:C2 → act:E1
```

Durations and readiness allowances are held in activities/services. Dependencies do not add them again.

## 12. Current state and constraints

### 12.1 Baseline CurrentState

| Field | Value |
|---|---|
| As of | 2026-09-26 05:00 IST |
| Location | `rail:CSMT` |
| Phase | `not_started` |
| Active service | null |
| Completed activities | empty |
| Decision allowance | 15 min |

### 12.2 Hard constraints

| Constraint ID | Required value |
|---|---|
| `constraint:party-size` | exactly 1 |
| `constraint:cash` | cash required ≤ ₹10,000 |
| `constraint:incremental-cost` | incremental cost ≤ ₹9,000 |
| `constraint:event-E1` | venue arrival ≤ 19:15 |
| `constraint:hotel-H1` | H1 starts from 12:00 through 21:00 inclusive and precedes E1 |
| `constraint:capacity` | known capacity ≥ 1 |
| `constraint:allowed-modes` | rail, air and road transfer allowed |
| `constraint:max-fixed-legs` | no more than 2 new fixed services |
| `constraint:max-transfer-legs` | no more than 8 transfer activities |
| `constraint:horizon` | final relevant activity by 2026-09-27 05:00 IST |

Default ranking preset is `cheapest`. Accessibility requirement is false for the hero.

## 13. Events

### 13.1 D1 — Required hero event

| Field | Value |
|---|---|
| Event ID | `event:D1` |
| Source / sequence | `replay:mumbai-goa-v2` / 1 |
| Expected trip version | 1 |
| Type | `SERVICE_TIMING_UPDATED` |
| Service | T1 |
| Observed/effective at | 2026-09-26 05:00 IST |
| New departure | 2026-09-26 09:00 IST |
| New arrival | 2026-09-26 18:30 IST |
| Provenance | synthetic replay D1 |

D1 changes effective times only. It is not represented as `delay_minutes=180` in the authoritative mutation.

### 13.2 Optional test events

| Event | Prerequisite state | Change | Expected use |
|---|---|---|---|
| D2 | D1 applied, version 2 | Cancel F3 | F2 remains feasible under original budget |
| D3 | D1 applied, version 2 | Change F3 to 15:40–16:55 | Venue 19:00, +15 min, at risk |
| D4 | D1 applied, version 2 | Change F3 to 15:56–17:11 | Venue 19:16, −1 min, infeasible |
| D5 | Baseline version 1 | Cancel T1 | Original chain blocked; flight recovery still evaluated |

D2–D4 are independent branches from the same version-2 state; do not apply them sequentially to one branch unless a separate compound-event test says so.

## 14. Required calculations

### 14.1 Baseline

```text
T1 arrival                    15:30
+ exit processing             00:20
+ C1                          01:10
+ H1 check-in                 00:20
+ C2                          00:30
= venue arrival               17:50

event cutoff                  19:15
- venue arrival               17:50
= slack                       +85 min
```

### 14.2 Delayed original plan

```text
T1 effective arrival          18:30
+ exit processing             00:20
+ C1                          01:10
+ H1 check-in                 00:20
+ C2                          00:30
= venue arrival               20:50

event cutoff                  19:15
- venue arrival               20:50
= slack                       -95 min
```

Hotel H1 starts at 20:00, within its inclusive latest start of 21:00. The hotel remains feasible while the wedding fails.

### 14.3 F2 path

```text
X1                            05:15–06:45
F2 readiness cutoff           08:00       pass by 75 min
F2                            10:00–11:15
GOX exit                      11:15–11:45
GOX→hotel                     11:45–12:45
H1                            12:45–13:05
C2                            13:05–13:35
venue arrival                 13:35
event slack                   +340 min

cash = 1200 + 6500 + 1500 + 500 = ₹9,700
increment = 9700 - 1300 = ₹8,400
```

### 14.4 F3 path

```text
X1                            05:15–06:45
F3 readiness cutoff           12:00       pass by 315 min
F3                            14:00–15:15
GOI exit                      15:15–15:45
GOI→hotel                     15:45–16:30
H1                            16:30–16:50
C2                            16:50–17:20
venue arrival                 17:20
event slack                   +115 min

cash = 1200 + 3800 + 1000 + 500 = ₹6,500
increment = 6500 - 1300 = ₹5,200
```

### 14.5 F4 path

```text
X1                            05:15–06:45
F4 readiness cutoff           14:30       pass by 465 min
F4                            16:30–17:45
GOX exit                      17:45–18:15
GOX→hotel                     18:15–19:15
H1                            19:15–19:35
C2                            19:35–20:05
venue arrival                 20:05
event slack                   -50 min

cash = 1200 + 2500 + 1500 + 500 = ₹5,700
increment = 5700 - 1300 = ₹4,400
```

F4 is rejected even though it costs less than F2/F3. H1 start 19:15 still passes its hotel window.

## 15. Canonical logical fixture manifest

This JSON is complete enough to generate the P0 fixture. Document 07 may rename or nest fields when creating executable schemas, but it must provide a deterministic migration from this manifest and preserve all values.

```json
{
  "schema_version": "fixture-spec-1.0",
  "scenario": {
    "id": "mumbai-goa-v2",
    "name": "Mumbai to Goa wedding recovery",
    "mode": "demo",
    "catalog_version": "catalog:mumbai-goa-v2",
    "currency": "INR",
    "display_timezone": "Asia/Kolkata",
    "replay_start": "2026-09-26T05:00:00+05:30",
    "decision_allowance_sec": 900,
    "search_horizon_end": "2026-09-27T05:00:00+05:30",
    "risk_threshold_sec": 1800,
    "truth_label": "SYNTHETIC SCENARIO — NOT BOOKABLE"
  },
  "provenance": [
    {
      "id": "prov:fixture:mumbai-goa-v2",
      "kind": "synthetic",
      "verification": "fixture",
      "observed_at": "2026-09-06T00:00:00+05:30",
      "retrieved_at": "2026-09-06T00:00:00+05:30",
      "valid_until": null,
      "source_ref": "document-04"
    },
    {
      "id": "prov:user:asha-state",
      "kind": "user_reported",
      "verification": "fixture",
      "observed_at": "2026-09-26T05:00:00+05:30",
      "retrieved_at": "2026-09-26T05:00:00+05:30",
      "valid_until": null,
      "source_ref": "fixture-current-state"
    },
    {
      "id": "prov:estimate:map-points",
      "kind": "estimate",
      "verification": "fixture",
      "observed_at": "2026-09-06T00:00:00+05:30",
      "retrieved_at": "2026-09-06T00:00:00+05:30",
      "valid_until": null,
      "source_ref": "illustrative-map-coordinates"
    },
    {
      "id": "prov:replay:D1",
      "kind": "synthetic",
      "verification": "fixture",
      "observed_at": "2026-09-26T05:00:00+05:30",
      "retrieved_at": "2026-09-26T05:00:00+05:30",
      "valid_until": null,
      "source_ref": "replay:mumbai-goa-v2"
    },
    {
      "id": "prov:guidance:rail-policy",
      "kind": "official_replay",
      "verification": "unverified",
      "observed_at": "2026-09-06T00:00:00+05:30",
      "retrieved_at": "2026-09-06T00:00:00+05:30",
      "valid_until": null,
      "source_ref": "audited-conflicting-official-guidance"
    }
  ],
  "locations": [
    {"id":"rail:CSMT","kind":"rail_station","name":"Chhatrapati Shivaji Maharaj Terminus","code":"CSMT","terminal":null,"lat":18.9398,"lon":72.8355,"provenance_id":"prov:estimate:map-points"},
    {"id":"rail:MAO","kind":"rail_station","name":"Madgaon Junction","code":"MAO","terminal":null,"lat":15.2670,"lon":73.9580,"provenance_id":"prov:estimate:map-points"},
    {"id":"airport:BOM:T2","kind":"airport_terminal","name":"Mumbai Airport Terminal 2","code":"BOM","terminal":"T2","lat":19.1000,"lon":72.8740,"provenance_id":"prov:estimate:map-points"},
    {"id":"airport:GOX:ARR","kind":"airport_terminal","name":"Manohar International Airport Arrivals","code":"GOX","terminal":"ARR","lat":15.7443,"lon":73.8602,"provenance_id":"prov:estimate:map-points"},
    {"id":"airport:GOI:ARR","kind":"airport_terminal","name":"Goa International Airport Arrivals","code":"GOI","terminal":"ARR","lat":15.3808,"lon":73.8314,"provenance_id":"prov:estimate:map-points"},
    {"id":"place:PANAJI_HOTEL","kind":"hotel","name":"Asha's fictional Panaji hotel","code":null,"terminal":null,"lat":15.4909,"lon":73.8278,"provenance_id":"prov:estimate:map-points"},
    {"id":"place:WEDDING_VENUE","kind":"venue","name":"Fictional Panaji wedding venue","code":null,"terminal":null,"lat":15.4800,"lon":73.8200,"provenance_id":"prov:estimate:map-points"}
  ],
  "policies": [
    {"id":"policy:fictional:flex-cab:v1","source_class":"synthetic","scope":"fixture-road-transfers","verification":"fixture","conflict":false,"selected_price_due":true,"abandon_before_pickup_fee_paise":0,"calculation_allowed":true,"provenance_id":"prov:fixture:mumbai-goa-v2"},
    {"id":"policy:fictional:hotel-retained:v1","source_class":"synthetic","scope":"booking:hotel-original","verification":"fixture","conflict":false,"paid_paise":300000,"additional_checkin_fee_paise":0,"calculation_allowed":true,"provenance_id":"prov:fixture:mumbai-goa-v2"},
    {"id":"policy:fictional:new-air:v1","source_class":"synthetic","scope":"fixture-recovery-flights","verification":"fixture","conflict":false,"listed_fare_due_if_selected":true,"additional_fee_paise":0,"calculation_allowed":true,"provenance_id":"prov:fixture:mumbai-goa-v2"},
    {"id":"policy:guidance:rail:v1","source_class":"official_guidance","scope":"booking:train-original","verification":"unverified","conflict":true,"calculation_allowed":false,"result":"needs_provider_confirmation","provenance_id":"prov:guidance:rail-policy"}
  ],
  "services": [
    {"id":"svc:T1:2026-09-26","display_code":"T1","mode":"rail","service_date":"2026-09-26","origin_id":"rail:CSMT","destination_id":"rail:MAO","scheduled_departure":"2026-09-26T06:00:00+05:30","scheduled_arrival":"2026-09-26T15:30:00+05:30","effective_departure":"2026-09-26T06:00:00+05:30","effective_arrival":"2026-09-26T15:30:00+05:30","origin_allowance_sec":1800,"exit_allowance_sec":1200,"capacity":1,"price_paise":180000,"price_state":"paid","status":"scheduled","policy_id":"policy:guidance:rail:v1","provenance_id":"prov:fixture:mumbai-goa-v2"},
    {"id":"svc:F2:2026-09-26","display_code":"F2","mode":"air","service_date":"2026-09-26","origin_id":"airport:BOM:T2","destination_id":"airport:GOX:ARR","scheduled_departure":"2026-09-26T10:00:00+05:30","scheduled_arrival":"2026-09-26T11:15:00+05:30","effective_departure":"2026-09-26T10:00:00+05:30","effective_arrival":"2026-09-26T11:15:00+05:30","origin_allowance_sec":7200,"exit_allowance_sec":1800,"capacity":2,"price_paise":650000,"price_state":"due_if_selected","status":"scheduled","policy_id":"policy:fictional:new-air:v1","provenance_id":"prov:fixture:mumbai-goa-v2"},
    {"id":"svc:F3:2026-09-26","display_code":"F3","mode":"air","service_date":"2026-09-26","origin_id":"airport:BOM:T2","destination_id":"airport:GOI:ARR","scheduled_departure":"2026-09-26T14:00:00+05:30","scheduled_arrival":"2026-09-26T15:15:00+05:30","effective_departure":"2026-09-26T14:00:00+05:30","effective_arrival":"2026-09-26T15:15:00+05:30","origin_allowance_sec":7200,"exit_allowance_sec":1800,"capacity":2,"price_paise":380000,"price_state":"due_if_selected","status":"scheduled","policy_id":"policy:fictional:new-air:v1","provenance_id":"prov:fixture:mumbai-goa-v2"},
    {"id":"svc:F4:2026-09-26","display_code":"F4","mode":"air","service_date":"2026-09-26","origin_id":"airport:BOM:T2","destination_id":"airport:GOX:ARR","scheduled_departure":"2026-09-26T16:30:00+05:30","scheduled_arrival":"2026-09-26T17:45:00+05:30","effective_departure":"2026-09-26T16:30:00+05:30","effective_arrival":"2026-09-26T17:45:00+05:30","origin_allowance_sec":7200,"exit_allowance_sec":1800,"capacity":2,"price_paise":250000,"price_state":"due_if_selected","status":"scheduled","policy_id":"policy:fictional:new-air:v1","provenance_id":"prov:fixture:mumbai-goa-v2"}
  ],
  "transfer_templates": [
    {"id":"xfer:X1","display_code":"X1","origin_id":"rail:CSMT","destination_id":"airport:BOM:T2","window_start":"2026-09-26T05:15:00+05:30","latest_start":"2026-09-26T05:15:00+05:30","duration_sec":5400,"capacity":4,"price_paise":120000,"accessibility":"unknown","policy_id":"policy:fictional:flex-cab:v1","provenance_id":"prov:fixture:mumbai-goa-v2"},
    {"id":"xfer:C1","display_code":"C1","origin_id":"rail:MAO","destination_id":"place:PANAJI_HOTEL","window_start":"2026-09-26T00:00:00+05:30","latest_start":"2026-09-26T22:00:00+05:30","duration_sec":4200,"capacity":4,"price_paise":80000,"accessibility":"unknown","policy_id":"policy:fictional:flex-cab:v1","provenance_id":"prov:fixture:mumbai-goa-v2"},
    {"id":"xfer:C2","display_code":"C2","origin_id":"place:PANAJI_HOTEL","destination_id":"place:WEDDING_VENUE","window_start":"2026-09-26T00:00:00+05:30","latest_start":"2026-09-26T23:00:00+05:30","duration_sec":1800,"capacity":4,"price_paise":50000,"accessibility":"unknown","policy_id":"policy:fictional:flex-cab:v1","provenance_id":"prov:fixture:mumbai-goa-v2"},
    {"id":"xfer:X-GOX-HOTEL","display_code":"X-GOX-HOTEL","origin_id":"airport:GOX:ARR","destination_id":"place:PANAJI_HOTEL","window_start":"2026-09-26T00:00:00+05:30","latest_start":"2026-09-26T23:00:00+05:30","duration_sec":3600,"capacity":4,"price_paise":150000,"accessibility":"unknown","policy_id":"policy:fictional:flex-cab:v1","provenance_id":"prov:fixture:mumbai-goa-v2"},
    {"id":"xfer:X-GOI-HOTEL","display_code":"X-GOI-HOTEL","origin_id":"airport:GOI:ARR","destination_id":"place:PANAJI_HOTEL","window_start":"2026-09-26T00:00:00+05:30","latest_start":"2026-09-26T23:00:00+05:30","duration_sec":2700,"capacity":4,"price_paise":100000,"accessibility":"unknown","policy_id":"policy:fictional:flex-cab:v1","provenance_id":"prov:fixture:mumbai-goa-v2"}
  ],
  "bookings": [
    {"id":"booking:train-original","state":"fictional","service_or_activity_ids":["svc:T1:2026-09-26"],"paid_paise":180000,"remaining_paise":0,"policy_id":"policy:guidance:rail:v1"},
    {"id":"booking:hotel-original","state":"fictional","service_or_activity_ids":["act:H1"],"paid_paise":300000,"remaining_paise":0,"policy_id":"policy:fictional:hotel-retained:v1"},
    {"id":"booking:cab-C1","state":"fictional","service_or_activity_ids":["act:C1"],"paid_paise":0,"remaining_paise":80000,"policy_id":"policy:fictional:flex-cab:v1"},
    {"id":"booking:cab-C2","state":"fictional","service_or_activity_ids":["act:C2"],"paid_paise":0,"remaining_paise":50000,"policy_id":"policy:fictional:flex-cab:v1"}
  ],
  "original_activities": [
    {"id":"act:T1","kind":"fixed_transport","service_id":"svc:T1:2026-09-26","location_id":null,"booking_id":"booking:train-original","hard":true,"planned_start":"2026-09-26T06:00:00+05:30","planned_end":"2026-09-26T15:30:00+05:30"},
    {"id":"act:T1-exit","kind":"processing","service_id":null,"location_id":"rail:MAO","booking_id":null,"hard":true,"duration_sec":1200,"planned_start":"2026-09-26T15:30:00+05:30","planned_end":"2026-09-26T15:50:00+05:30"},
    {"id":"act:C1","kind":"flexible_transfer","transfer_template_id":"xfer:C1","location_id":null,"booking_id":"booking:cab-C1","hard":true,"planned_start":"2026-09-26T15:50:00+05:30","planned_end":"2026-09-26T17:00:00+05:30"},
    {"id":"act:H1","kind":"hotel_checkin","location_id":"place:PANAJI_HOTEL","booking_id":"booking:hotel-original","hard":true,"earliest_start":"2026-09-26T12:00:00+05:30","latest_start":"2026-09-26T21:00:00+05:30","duration_sec":1200,"planned_start":"2026-09-26T17:00:00+05:30","planned_end":"2026-09-26T17:20:00+05:30"},
    {"id":"act:C2","kind":"flexible_transfer","transfer_template_id":"xfer:C2","location_id":null,"booking_id":"booking:cab-C2","hard":true,"planned_start":"2026-09-26T17:20:00+05:30","planned_end":"2026-09-26T17:50:00+05:30"},
    {"id":"act:E1","kind":"commitment","location_id":"place:WEDDING_VENUE","booking_id":null,"hard":true,"start_at":"2026-09-26T19:30:00+05:30","readiness_allowance_sec":900,"latest_arrival":"2026-09-26T19:15:00+05:30"}
  ],
  "original_dependencies": [
    {"id":"dep:T1-to-exit","from_id":"act:T1","to_id":"act:T1-exit","buffer_sec":0,"reason":"exit_after_arrival"},
    {"id":"dep:exit-to-C1","from_id":"act:T1-exit","to_id":"act:C1","buffer_sec":0,"reason":"transfer_after_exit"},
    {"id":"dep:C1-to-H1","from_id":"act:C1","to_id":"act:H1","buffer_sec":0,"reason":"hotel_after_transfer"},
    {"id":"dep:H1-to-C2","from_id":"act:H1","to_id":"act:C2","buffer_sec":0,"reason":"venue_transfer_after_checkin"},
    {"id":"dep:C2-to-E1","from_id":"act:C2","to_id":"act:E1","buffer_sec":0,"reason":"arrive_before_commitment"}
  ],
  "current_state": {
    "as_of":"2026-09-26T05:00:00+05:30",
    "location_id":"rail:CSMT",
    "phase":"not_started",
    "active_service_id":null,
    "completed_activity_ids":[],
    "next_recovery_point_id":null,
    "provenance_id":"prov:user:asha-state"
  },
  "constraints": {
    "party_size":1,
    "max_cash_required_paise":1000000,
    "max_incremental_cost_paise":900000,
    "allowed_modes":["rail","air","road_transfer"],
    "required_commitment_ids":["act:H1","act:E1"],
    "accessibility_required":false,
    "ranking_preset":"cheapest",
    "max_new_fixed_legs":2,
    "max_transfer_legs":8,
    "horizon_end":"2026-09-27T05:00:00+05:30",
    "risk_threshold_sec":1800
  },
  "baseline_money_items": [
    {"id":"money:T1-paid","booking_id":"booking:train-original","category":"sunk_cost","payment_state":"paid","amount_paise":180000,"provenance_id":"prov:fixture:mumbai-goa-v2"},
    {"id":"money:H1-paid","booking_id":"booking:hotel-original","category":"sunk_cost","payment_state":"paid","amount_paise":300000,"provenance_id":"prov:fixture:mumbai-goa-v2"},
    {"id":"money:C1-due","booking_id":"booking:cab-C1","category":"retained_charge","payment_state":"due","amount_paise":80000,"provenance_id":"prov:fixture:mumbai-goa-v2"},
    {"id":"money:C2-due","booking_id":"booking:cab-C2","category":"retained_charge","payment_state":"due","amount_paise":50000,"provenance_id":"prov:fixture:mumbai-goa-v2"},
    {"id":"money:T1-potential-refund","booking_id":"booking:train-original","category":"potential_refund","payment_state":"potential","amount_paise":null,"provenance_id":"prov:guidance:rail-policy"}
  ],
  "events": [
    {
      "event_id":"event:D1",
      "source_id":"replay:mumbai-goa-v2",
      "source_sequence":1,
      "expected_trip_version":1,
      "type":"SERVICE_TIMING_UPDATED",
      "service_id":"svc:T1:2026-09-26",
      "observed_at":"2026-09-26T05:00:00+05:30",
      "effective_at":"2026-09-26T05:00:00+05:30",
      "new_departure_at":"2026-09-26T09:00:00+05:30",
      "new_arrival_at":"2026-09-26T18:30:00+05:30",
      "provenance_id":"prov:replay:D1"
    }
  ],
  "expected_outcomes": {
    "baseline":{"venue_arrival":"2026-09-26T17:50:00+05:30","event_slack_sec":5100,"status":"feasible"},
    "after_D1":{"venue_arrival":"2026-09-26T20:50:00+05:30","event_slack_sec":-5700,"status":"infeasible","hotel_start":"2026-09-26T20:00:00+05:30"},
    "plans":[
      {"id":"plan:F2:v2","sequence":["xfer:X1","svc:F2:2026-09-26","process:F2-exit","xfer:X-GOX-HOTEL","act:H1","xfer:C2","act:E1"],"cash_required_paise":970000,"incremental_cost_paise":840000,"venue_arrival":"2026-09-26T13:35:00+05:30","event_slack_sec":20400,"changed_original_booking_count":2,"valid_until":"2026-09-26T05:15:00+05:30","validity":"feasible","rank_fastest":1,"rank_cheapest":2},
      {"id":"plan:F3:v2","sequence":["xfer:X1","svc:F3:2026-09-26","process:F3-exit","xfer:X-GOI-HOTEL","act:H1","xfer:C2","act:E1"],"cash_required_paise":650000,"incremental_cost_paise":520000,"venue_arrival":"2026-09-26T17:20:00+05:30","event_slack_sec":6900,"changed_original_booking_count":2,"valid_until":"2026-09-26T05:15:00+05:30","validity":"feasible","rank_fastest":2,"rank_cheapest":1},
      {"id":"plan:F4:v2","sequence":["xfer:X1","svc:F4:2026-09-26","process:F4-exit","xfer:X-GOX-HOTEL","act:H1","xfer:C2","act:E1"],"cash_required_paise":570000,"incremental_cost_paise":440000,"venue_arrival":"2026-09-26T20:05:00+05:30","event_slack_sec":-3000,"changed_original_booking_count":2,"valid_until":"2026-09-26T05:15:00+05:30","validity":"infeasible","reason_codes":["HARD_DEADLINE_MISSED"]},
      {"id":"plan:WAIT-T1:v2","sequence":["svc:T1:2026-09-26","process:T1-exit","xfer:C1","act:H1","xfer:C2","act:E1"],"cash_required_paise":130000,"incremental_cost_paise":0,"venue_arrival":"2026-09-26T20:50:00+05:30","event_slack_sec":-5700,"changed_original_booking_count":0,"valid_until":"2026-09-26T08:30:00+05:30","validity":"infeasible","reason_codes":["HARD_DEADLINE_MISSED"]}
    ],
    "plan_valid_until_inclusive":false,
    "potential_train_refund_paise":null
  }
}
```

## 16. Expected plan money items

### F2

| ID | Category/state | Amount |
|---|---|---:|
| `money:F2:X1` | new_purchase/due | ₹1,200 |
| `money:F2:fare` | new_purchase/due | ₹6,500 |
| `money:F2:GOX-hotel` | new_purchase/due | ₹1,500 |
| `money:F2:C2` | retained_charge/due | ₹500 |

### F3

| ID | Category/state | Amount |
|---|---|---:|
| `money:F3:X1` | new_purchase/due | ₹1,200 |
| `money:F3:fare` | new_purchase/due | ₹3,800 |
| `money:F3:GOI-hotel` | new_purchase/due | ₹1,000 |
| `money:F3:C2` | retained_charge/due | ₹500 |

### F4

| ID | Category/state | Amount |
|---|---|---:|
| `money:F4:X1` | new_purchase/due | ₹1,200 |
| `money:F4:fare` | new_purchase/due | ₹2,500 |
| `money:F4:GOX-hotel` | new_purchase/due | ₹1,500 |
| `money:F4:C2` | retained_charge/due | ₹500 |

Every flight plan abandons original C1 before pickup with the fixture’s explicit zero fee. It retains H1 and C2. T1’s potential refund remains null and does not appear as a negative money item.

## 17. Expected constraint checks

| Plan/check | Observed | Required | Result/reason |
|---|---|---|---|
| F2 event arrival | 13:35 | ≤19:15 | pass |
| F2 cash | ₹9,700 | ≤₹10,000 | pass |
| F2 incremental | ₹8,400 | ≤₹9,000 | pass |
| F3 event arrival | 17:20 | ≤19:15 | pass |
| F3 cash | ₹6,500 | ≤₹10,000 | pass |
| F3 incremental | ₹5,200 | ≤₹9,000 | pass |
| F4 event arrival | 20:05 | ≤19:15 | fail / `HARD_DEADLINE_MISSED` |
| Wait event arrival | 20:50 | ≤19:15 | fail / `HARD_DEADLINE_MISSED` |

All services/transfers have sufficient known capacity in the hero. Accessibility is not required, so unknown accessibility does not block this fixture.

## 18. Ranking outcomes

Only feasible plans participate in ranking.

| Preset | Expected order | Tie-breaking observation |
|---|---|---|
| `cheapest` | F3, F2 | Cash ₹6,500 before ₹9,700 |
| `fastest` | F2, F3 | Venue 13:35 before 17:20 |
| `fewest_changes` | F3, F2 | Both change two original bookings; lower cash breaks tie |

F4 and waiting must never appear in the valid order.

## 19. Required perturbation matrix

Each row starts from a named clean branch. It must not inherit unrelated changes from another row.

| Case ID | Starting branch | Mutation | Expected valid set/order | Required extra result |
|---|---|---|---|---|
| FX-01 | after D1 | Cash limit ₹7,000 | F3 only | F2 fails `CASH_LIMIT_EXCEEDED` |
| FX-02 | after D1 | Cash limit ₹5,000 | none | Complete result says no feasible plan in evaluated catalog; minimum P1 cash relaxation ₹6,500 |
| FX-03 | after D1 | Cancel F3 | F2 only | F3 fails `SERVICE_CANCELLED` |
| FX-04 | after D1 | F3 times 15:40–16:55 | F3 remains feasible | Venue 19:00; +15 min; `at_risk` |
| FX-05 | after D1 | F3 times 15:56–17:11 | F3 rejected | Venue 19:16; −1 min; `HARD_DEADLINE_MISSED` |
| FX-06 | baseline | Cancel T1 | F2, F3 | Original chain `blocked`; recovery remains possible |
| FX-07 | after D1 | F3 capacity 0 | F2 only | F3 fails `CAPACITY_INSUFFICIENT` |
| FX-08 | after D1 | F3 capacity null | F2 certified; F3 unknown | F3 uses `CAPACITY_UNKNOWN`, not false zero |
| FX-09 | after D1 | Accessibility required true | none certified | Road transfers have `ACCESSIBILITY_UNKNOWN` |
| FX-10 | after D1 | Replay clock reaches 05:15 before adoption | F2/F3/F4 previews expire; wait remains rejected on event deadline | Feasible flight previews return `STALE_PLAN`; regenerate from new current state |
| FX-11 | after D1 | Current phase onboard T1, no modeled recovery point | no CSMT flight suggestions | `UNSUPPORTED_CURRENT_STATE` or `needs_input` before search |
| FX-12 | baseline | Apply identical D1 twice | same version/content after retry | second disposition duplicate; no extra 180 min |
| FX-13 | baseline | Reuse D1 ID with other times | no mutation | `EVENT_ID_CONFLICT` |
| FX-14 | after D1 | Send new event with expected version 1 | no mutation | `VERSION_CONFLICT` |
| FX-15 | after D1 | Stop search before all bounded services evaluated | labeled partial plans only | `partial_search`; no cheapest/fastest global claim |

For FX-11, the invalid/incomplete onboard state must be handled before candidate generation. The system must not repair it by assigning `rail:CSMT` as the traveler’s location.

## 20. Negative fixture rules

The implementation test suite must also produce small invalid copies of the manifest:

| Negative ID | Change | Expected validation |
|---|---|---|
| NEG-01 | Remove timezone offset from a service time | Reject timestamp |
| NEG-02 | Duplicate a location or activity ID | Reject uniqueness violation |
| NEG-03 | Add dependency E1 → T1 | Reject cyclic graph |
| NEG-04 | Reference missing transfer/location/policy | Reject referential integrity |
| NEG-05 | Set transfer duration to 0 or negative | Reject duration |
| NEG-06 | Set price/capacity negative | Reject range |
| NEG-07 | Set service arrival before departure | Reject chronology |
| NEG-08 | Use fractional or Boolean paise | Reject money type |
| NEG-09 | Set party size 2 | Reject unsupported P0 party size |
| NEG-10 | Mark plan `bookable=true` | Reject P0 invariant |
| NEG-11 | Set hotel earliest start after latest start | Reject window |
| NEG-12 | Duplicate a MoneyItem ID in one plan | Reject financial uniqueness |
| NEG-13 | Give F3 GOI arrival but use GOX transfer | Reject location continuity |
| NEG-14 | Set CurrentState onboard with no active service | Reject current-state invariant |
| NEG-15 | Apply unsupported weather event as if it changes times | Reject event union/type |

## 21. Fixture-derived UI copy

The UI may phrase these messages more naturally while preserving values and reason codes.

| Situation | Required factual content |
|---|---|
| D1 impact | “T1 now arrives at 18:30. Your current plan reaches the venue at 20:50, 95 minutes after your 19:15 arrival cutoff.” |
| Hotel status after D1 | “Hotel check-in starts at 20:00, within the scenario’s 21:00 latest start.” |
| F3 recommendation | “Cheapest feasible scenario plan: ₹6,500 still to pay; ₹5,200 above your original remaining spend; venue arrival 17:20.” |
| F2 trade-off | “Arrives 3 hours 45 minutes earlier than F3 and requires ₹3,200 more cash.” |
| F4 rejection | “Costs less than F3 but reaches the venue at 20:05, 50 minutes after the required arrival.” |
| ₹5,000 no solution | “No feasible plan in the evaluated catalog under a ₹5,000 cash limit.” |
| Adoption | “Plan adopted inside ResiliTrip. No flight, train, cab or hotel booking was changed.” |
| Rail policy | “Potential refund unknown. Verify the applicable terms with the provider.” |

The F2 comparison uses ₹9,700 − ₹6,500 = ₹3,200 and 17:20 − 13:35 = 3 hours 45 minutes.

## 22. Fixture validation checklist

Before using this fixture in a demo or code generation, verify:

- JSON parses and IDs are unique.
- Every reference resolves.
- Service and transfer paths are location-continuous.
- All timestamps include offsets and normalize chronologically.
- Original dependency graph is acyclic.
- Baseline and D1 calculations match §14.
- F2/F3/F4/wait money totals match §16.
- Constraint results match §17.
- Ranking matches §18.
- Perturbations produce §19 results from clean branches.
- Potential refund remains null and outside cash.
- F2/F3/F4 validity is exclusive at 05:15; wait-path validity is exclusive at T1’s 08:30 readiness cutoff.
- Every visible source label remains synthetic/user-reported/estimate as defined.
- No fixture field is described as a current real service fact.

## 23. Ownership and approval

| Area | Owner | Reviewer |
|---|---|---|
| Services, activities, time arithmetic | A — Domain/impact | B |
| Candidate paths, money and ranking | B — Planner/finance | A |
| Display coordinates and UI copy | C — Product/UI | A |
| Manifest parsing, versioning and event branches | D — API/integration | A/B |

This fixture is ready to lock when its manifest parses, reference arithmetic passes, domain IDs conform to Document 03 and A/B independently reproduce every plan without reading the expected result first.

After approval, create **Document 05 — Algorithm and Recovery-Planning Specification**. It must compute these outcomes from the atomic manifest rather than encode them as final recommendations.
