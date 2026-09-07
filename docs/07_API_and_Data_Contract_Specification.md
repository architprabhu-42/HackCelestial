# ResiliTrip — API and Data Contract Specification

**Document:** 07 of the ResiliTrip implementation pack  
**Version:** 1.0  
**Contract version:** `resilitrip-api-1.0`  
**Date:** 6 September 2026  
**Status:** Proposed code-generation baseline  
**Depends on:** Documents 01–06  
**Feeds:** UX Specification, Test Strategy, implementation backlog and generated OpenAPI/TypeScript artifacts

## 1. Purpose

This document fixes the exact P0 transport and serialization contract for ResiliTrip. It defines:

- URL and HTTP conventions;
- strict scalar formats and collection bounds;
- every request, response and domain DTO;
- discriminated unions for activities, policies, events and evidence values;
- version, idempotency and plan-validity semantics;
- error envelopes and status-code mapping;
- OpenAPI stability and TypeScript generation;
- the migration from Document 04’s logical manifest to the executable fixture; and
- contract acceptance criteria.

The implementation may organize Python files differently, but externally visible JSON and semantics must conform to this document. A contract change requires a contract-version decision and regenerated artifacts; it cannot be made only in frontend code.

## 2. Contract principles

| Contract ID | Rule |
|---|---|
| API-G01 | The backend is authoritative for time, money, feasibility, ranking and plan identity |
| API-G02 | All models reject unknown fields unless this document explicitly declares a map |
| API-G03 | Input unions use an explicit discriminator; field presence is never used to guess a subtype |
| API-G04 | Missing and null are different; null is accepted only where unknown is a valid domain value |
| API-G05 | Money is strict integer paise; booleans and floats are invalid |
| API-G06 | Every instant contains a numeric UTC offset; naive timestamps are invalid |
| API-G07 | A response represents one coherent trip/catalog version pair |
| API-G08 | Domain results use 200 responses even when no feasible plan exists |
| API-G09 | Conflicts and validation failures never partially mutate state |
| API-G10 | P0 requests cannot submit authoritative plan totals, status, capacity or availability overrides |

## 3. API surface and media type

- Base path: `/api/v1`
- JSON media type: `application/json`
- Character encoding: UTF-8
- Maximum JSON request body: 262,144 bytes
- OpenAPI path: `/api/v1/openapi.json` in development; disabled or local-only in packaged demo if desired
- Interactive docs: development-only
- Health paths: `/api/health/live` and `/api/health/ready`

No GraphQL, WebSocket, SSE, multipart upload or provider callback exists in P0.

## 4. HTTP conventions

### 4.1 Required response headers

| Header | Value/rule |
|---|---|
| `Content-Type` | `application/json; charset=utf-8` for JSON responses |
| `X-Request-ID` | Server-generated opaque ID unless a valid client value is accepted |
| `Cache-Control` | `no-store` for trip, plan, event and adoption resources |
| `ETag` | Weak trip-view ETag on snapshot-bearing reads/responses |

Trip-view ETag format:

```text
W/"trip:{trip_id}:v{trip_version}:catalog:{catalog_version}"
```

ETag is a cache/debug aid. P0 mutation concurrency uses the explicit `expected_trip_version` field, not `If-Match`.

### 4.2 Request IDs

Clients may send `X-Request-ID` matching `^[A-Za-z0-9._-]{8,80}$`. Invalid client values are ignored and replaced. Request IDs are not idempotency keys.

### 4.3 Success envelope policy

Resource responses are not wrapped in a generic `data` object. Each operation returns its named response model so OpenAPI and generated TypeScript remain specific. All failures use the common `ProblemResponse`.

### 4.4 Timeouts and client retry

- Reads may be retried.
- Plan generation may be explicitly retried against the same version.
- Mutation clients must not automatically create a new command/event ID on retry.
- Event retry uses the same `event_id` and identical canonical payload.
- Adoption is not automatically retried after an ambiguous client/network failure; fetch the trip and plan state first.

## 5. Scalar formats

### 5.1 Identifier

`EntityId` is a case-sensitive string:

```text
pattern: ^[A-Za-z0-9][A-Za-z0-9:._-]{0,127}$
minLength: 1
maxLength: 128
```

IDs are opaque. Prefixes aid humans but never determine subtype.

Server-generated trip, planner-run and adoption IDs use `trip:{uuid4}`, `run:{uuid4}` and `adoption:{uuid4}` with lowercase RFC 4122 UUID text from the standard library. Plan IDs are deterministic within a trip/version and may retain fixture-readable values such as `plan:F3:v2`; their storage/API identity is the composite `(trip_id, plan_id)`, not `plan_id` alone.

Plan ID construction uses `plan:{primary-action-code}:v{trip_version}` when that base identifies one sequence in the candidate set. If two different signatures share the base, append `:{first-8-signature-hex}` to every colliding base. The full signature, not the readable ID, remains the equality test.

### 5.2 Human label

`DisplayLabel` is a string of 1–120 Unicode characters after the client has trimmed form whitespace. The API rejects an empty/whitespace-only value and control characters. HTML is not accepted as markup; React renders it as text.

### 5.3 Timestamp

`AwareDateTime` is an RFC 3339/ISO 8601 datetime string with seconds and an explicit `Z` or numeric offset. Examples:

- valid: `2026-09-26T05:00:00+05:30`
- valid: `2026-09-25T23:30:00Z`
- invalid: `2026-09-26T05:00:00`
- invalid: `26/09/2026 05:00`

The server compares normalized UTC instants. Hero responses serialize in `Asia/Kolkata` with `+05:30` to preserve presentation clarity.

### 5.4 Date

`ServiceDate` uses `YYYY-MM-DD` and represents the local advertised service date.

### 5.5 Money

`MoneyPaise` is a strict JSON integer from 0 through 100,000,000 inclusive. `NullableMoneyPaise` additionally permits null when an amount is genuinely unknown. Negative amounts, booleans, numeric strings and fractions are invalid.

Incremental cost is computed output and may be negative, so `SignedMoneyPaise` is a strict integer from −100,000,000 through 100,000,000.

### 5.6 Duration and slack

- `DurationSec`: strict integer from 0 through 86,400.
- `PositiveDurationSec`: strict integer from 1 through 86,400.
- `SlackSec`: strict signed integer from −172,800 through 172,800.

Document 04’s fixture values are within these P0 bounds. Search still enforces its separate horizon.

### 5.7 Coordinates

- latitude: finite number from −90 through 90;
- longitude: finite number from −180 through 180.

Coordinates are display data and cannot determine duration or continuity.

### 5.8 Boolean strictness

All booleans must be JSON `true`/`false`. Integers `0`/`1` and strings are invalid.

## 6. Collection bounds

| Collection | Minimum | Maximum | Additional rule |
|---|---:|---:|---|
| Travelers | 1 | 1 | P0 party size remains one |
| Locations | 1 | 100 | IDs unique |
| Services | 0 | 50 | IDs unique |
| Transfer templates | 0 | 50 | IDs unique |
| Activities per itinerary | 1 | 20 | IDs unique |
| Dependencies | 0 | 80 | IDs unique; endpoints resolve; DAG |
| Bookings | 0 | 50 | IDs unique |
| Policies | 0 | 50 | IDs unique |
| Provenance records | 1 | 100 | IDs unique |
| Money items per plan/baseline | 0 | 100 | IDs unique |
| Constraint checks per plan | 0 | 200 | Constraint IDs unique within plan |
| Root event IDs per impact | 1 | 20 | IDs unique |
| Causal activity path | 1 | 20 | Ordered and contiguous |
| Allowed modes | 1 | 4 | Values unique |
| Required commitments | 1 | 20 | Values unique |
| Primary displayed frontier plans | 0 | 3 | Server-selected |
| Representative rejected plans | 0 | 10 | Server-selected; aggregate counts preserve remainder |

The 256 KB request limit applies in addition to these semantic bounds.

## 7. Shared model configuration

All Pydantic request/domain DTOs use the equivalent of:

```python
from pydantic import BaseModel, ConfigDict

class ContractModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        validate_assignment=True,
        frozen=True,
    )
```

Database ORM classes are not response models. Output DTOs are constructed explicitly from validated domain/application records.

Validators additionally enforce:

- timezone-aware datetimes;
- finite coordinate values;
- unique IDs/list members;
- cross-references and subtype rules;
- chronological windows and services;
- current-state invariants;
- DAG acyclicity;
- catalog/trip version agreement.

## 8. Enumerations

All enum values serialize as the exact lowercase or uppercase strings shown.

| Enum | Values |
|---|---|
| `TripMode` | `demo` |
| `CurrencyCode` | `INR` |
| `LocationKind` | `rail_station`, `airport_terminal`, `hotel`, `venue`, `generic_point` |
| `TransportMode` | `rail`, `air`, `bus`, `road_transfer` |
| `FixedServiceMode` | `rail`, `air`, `bus` |
| `TravelerPhase` | `not_started`, `at_location`, `onboard`, `completed` |
| `ServiceStatus` | `scheduled`, `delayed`, `cancelled` |
| `AccessibilityState` | `suitable`, `unsuitable`, `unknown` |
| `BookingState` | `fictional`, `user_reported`, `provider_confirmed`, `cancelled` |
| `RankingPreset` | `cheapest`, `fastest`, `fewest_changes` |
| `RankingReasonCode` | `LOWEST_CASH_ON_FRONTIER`, `EARLIEST_ARRIVAL_ON_FRONTIER`, `FEWEST_CHANGES_ON_FRONTIER`, `TIE_BROKEN_BY_CASH`, `TIE_BROKEN_BY_ARRIVAL`, `TIE_BROKEN_BY_CHANGES`, `TIE_BROKEN_BY_PLAN_ID` |
| `ServicePriceState` | `paid`, `due_if_selected` |
| `PolicyKind` | `flexible_transfer_fictional`, `hotel_retained_fictional`, `new_fixed_service_fictional`, `provider_guidance` |
| `PolicySourceClass` | `synthetic`, `official_guidance`, `user_reported` |
| `ActivityKind` | `fixed_transport`, `flexible_transfer`, `processing`, `hotel_checkin`, `commitment` |
| `FeasibilityStatus` | `feasible`, `at_risk`, `infeasible`, `blocked`, `unknown` |
| `PlanLifecycleStatus` | `preview`, `adopted`, `stale` |
| `PlannerResultStatus` | `complete`, `no_feasible_catalog_plan`, `needs_input`, `partial_search`, `error` |
| `EventType` | `SERVICE_TIMING_UPDATED`, `SERVICE_CANCELLED` |
| `EventDisposition` | `applied`, `duplicate` |
| `ProvenanceKind` | `synthetic`, `user_reported`, `official_replay`, `authorized_live`, `estimate` |
| `VerificationState` | `unverified`, `fixture`, `provider_confirmed` |
| `MoneyCategory` | `retained_charge`, `new_purchase`, `mandatory_fee`, `potential_refund`, `received_refund`, `sunk_cost` |
| `PaymentState` | `paid`, `due`, `potential` |
| `MutationKind` | `created`, `event`, `constraints`, `current_state`, `itinerary_edit`, `adoption`, `reset` |
| `ProviderActionStatus` | `not_started` |
| `ProviderKey` | `indian_rail_enquiry`, `airline_or_ota`, `hotel`, `local_transfer` |

`DomainReasonCode` contains exactly the 27 domain codes in Document 03. `ApiErrorCode` contains the conflict codes that can cross the HTTP failure boundary plus the API validation/infrastructure codes in §34. These are separate generated enums, not arbitrary text.

## 9. Provenance contracts

### 9.1 `ProvenanceRecord`

| Field | Type | Required | Null | Rules |
|---|---|---:|---:|---|
| `id` | `EntityId` | yes | no | unique in catalog/trip view |
| `kind` | `ProvenanceKind` | yes | no | exact enum |
| `verification` | `VerificationState` | yes | no | does not imply freshness |
| `observed_at` | `AwareDateTime` | yes | no | source observation time |
| `retrieved_at` | `AwareDateTime` | yes | no | must be ≥ observed time unless fixture explicitly records clock skew error and is rejected |
| `valid_until` | `AwareDateTime` | yes | yes | exclusive when present; may be at/before retrieval to represent already-stale evidence |
| `source_ref` | string | yes | no | 1–200 chars; no arbitrary server-fetch behavior |

### 9.2 `FieldProvenanceRef`

| Field | Type | Rule |
|---|---|---|
| `field_path` | string | 1–160 chars; JSON-pointer-like path relative to owning record |
| `provenance_id` | `EntityId` | must resolve |

Every consequential record has `provenance_id` as its default source and `field_provenance: FieldProvenanceRef[]` for exceptions. Duplicate `field_path` overrides are invalid.

## 10. Location and traveler contracts

### 10.1 `TravelerProfile`

| Field | Type | Required | Rule |
|---|---|---:|---|
| `party_size` | strict integer | yes | exactly 1 |
| `display_name` | `DisplayLabel` | yes | nullable; fictional alias only |
| `accessibility_required` | strict boolean | yes | duplicates the declared traveler need, while Constraints owns evaluation setting; values must match |

### 10.2 `Location`

| Field | Type | Required | Null |
|---|---|---:|---:|
| `id` | `EntityId` | yes | no |
| `kind` | `LocationKind` | yes | no |
| `name` | `DisplayLabel` | yes | no |
| `code` | string 1–16 | yes | yes |
| `terminal` | string 1–24 | yes | yes |
| `latitude` | coordinate | yes | no |
| `longitude` | coordinate | yes | no |
| `provenance_id` | `EntityId` | yes | no |
| `field_provenance` | list | yes | no; may be empty |

Airport terminals require non-null `code` and `terminal`. Rail stations require non-null `code`. Hotel/venue/generic point may use null for both.

### 10.3 `CurrentState`

| Field | Type | Required | Null | Rule |
|---|---|---:|---:|---|
| `as_of` | `AwareDateTime` | yes | no | authoritative replay/current instant |
| `location_id` | `EntityId` | yes | yes | null only for `onboard` with modeled recovery point or `completed` |
| `phase` | `TravelerPhase` | yes | no | discriminator for cross-field rules |
| `active_service_id` | `EntityId` | yes | yes | required only for `onboard` |
| `completed_activity_ids` | `EntityId[]` | yes | no | unique; resolve in active itinerary |
| `next_recovery_point_id` | `EntityId` | yes | yes | allowed only for `onboard`; must resolve to location |
| `provenance_id` | `EntityId` | yes | no | must resolve |

Rules:

- `not_started` and `at_location` require `location_id` and null active service/recovery point.
- `onboard` requires `active_service_id`; a missing recovery point is structurally allowed but planner returns `needs_input`.
- `completed` requires null active service and may retain final location.
- `as_of` cannot move backwards in a normal update; reset may restore the fixture time under a new version.

## 11. Immutable catalog contracts

### 11.1 `ServiceDefinition`

The catalog stores scheduled facts only. Event-mutated effective facts are in `EffectiveServiceState` (§15).

| Field | Type | Required | Null | Rule |
|---|---|---:|---:|---|
| `id` | `EntityId` | yes | no | one dated instance |
| `display_code` | string 1–24 | yes | no | presentation only |
| `mode` | `FixedServiceMode` | yes | no | no road transfer |
| `service_date` | `ServiceDate` | yes | no | local advertised date |
| `origin_id` | `EntityId` | yes | no | resolves to location |
| `destination_id` | `EntityId` | yes | no | resolves and differs from origin |
| `scheduled_departure` | `AwareDateTime` | yes | no | normalized chronology |
| `scheduled_arrival` | `AwareDateTime` | yes | no | strictly after departure |
| `origin_allowance_sec` | `DurationSec` | yes | no | boarding/readiness allowance |
| `exit_allowance_sec` | `DurationSec` | yes | no | materialized once after use |
| `capacity` | strict integer ≥0 | yes | yes | null means unknown |
| `price_paise` | `MoneyPaise` | yes | yes | null means unknown |
| `price_state` | `paid` or `due_if_selected` | yes | no | catalog commercial intent |
| `policy_id` | `EntityId` | yes | no | resolves |
| `provenance_id` | `EntityId` | yes | no | default source |
| `field_provenance` | list | yes | no | may be empty |

### 11.2 `TransferTemplate`

| Field | Type | Required | Null | Rule |
|---|---|---:|---:|---|
| `id` | `EntityId` | yes | no | directed option |
| `display_code` | string 1–32 | yes | no | presentation only |
| `origin_id` | `EntityId` | yes | no | resolves |
| `destination_id` | `EntityId` | yes | no | resolves, differs from origin |
| `window_start` | `AwareDateTime` | yes | no | earliest start |
| `latest_start` | `AwareDateTime` | yes | no | ≥ window start; inclusive scheduling boundary |
| `duration_sec` | `PositiveDurationSec` | yes | no | deterministic fixture value |
| `capacity` | strict integer ≥0 | yes | yes | null unknown |
| `price_paise` | `MoneyPaise` | yes | yes | null unknown |
| `accessibility` | `AccessibilityState` | yes | no | exact enum |
| `policy_id` | `EntityId` | yes | no | resolves |
| `provenance_id` | `EntityId` | yes | no | default source |
| `field_provenance` | list | yes | no | may be empty |

### 11.3 Policy discriminated union

Every policy has common fields:

| Field | Type | Rule |
|---|---|---|
| `id` | `EntityId` | unique |
| `policy_kind` | discriminator | one subtype below |
| `source_class` | `synthetic`, `official_guidance`, `user_reported` | exact enum local to policies |
| `scope` | string 1–160 | human-auditable scope |
| `verification` | `VerificationState` | exact enum |
| `conflict` | strict boolean | conflicting official guidance remains true |
| `calculation_allowed` | strict boolean | false prevents monetary calculation |
| `provenance_id` | `EntityId` | resolves |

Subtypes:

| `policy_kind` | Additional exact fields |
|---|---|
| `flexible_transfer_fictional` | `selected_price_due: true`, `abandon_before_pickup_fee_paise: MoneyPaise` |
| `hotel_retained_fictional` | `paid_paise: MoneyPaise`, `additional_checkin_fee_paise: MoneyPaise` |
| `new_fixed_service_fictional` | `listed_fare_due_if_selected: true`, `additional_fee_paise: MoneyPaise` |
| `provider_guidance` | `result: "needs_provider_confirmation"`, `required_inputs: string[]`, `exclusions: string[]` |

`provider_guidance` requires `calculation_allowed=false`. The fictional subtypes require `source_class=synthetic`, `verification=fixture`, `conflict=false`, and `calculation_allowed=true`.

### 11.4 `ServiceCatalog`

| Field | Type | Rule |
|---|---|---|
| `schema_version` | literal `resilitrip-api-1.0` | required |
| `catalog_version` | `EntityId` | immutable identity |
| `scenario_id` | `EntityId` | nullable for manual catalog |
| `currency` | literal `INR` | required |
| `display_timezone` | literal `Asia/Kolkata` in P0 | required |
| `locations` | `Location[]` | bounds/unique/reference rules |
| `services` | `ServiceDefinition[]` | bounds/unique/reference rules |
| `transfer_templates` | `TransferTemplate[]` | bounds/unique/reference rules |
| `policies` | `PolicyRecord[]` | bounds/unique/reference rules |
| `provenance` | `ProvenanceRecord[]` | bounds/unique/reference rules |

The catalog does not contain expected results, trip bookings, current state or event-mutated effective service state.

## 12. Booking and money contracts

### 12.1 `Booking`

| Field | Type | Rule |
|---|---|---|
| `id` | `EntityId` | unique |
| `state` | `BookingState` | external knowledge only |
| `service_or_activity_ids` | `EntityId[]` | 1–20, unique; resolve |
| `paid_paise` | `MoneyPaise` | historical context |
| `remaining_paise` | `MoneyPaise` | future baseline charge |
| `policy_id` | `EntityId` | resolves |
| `provenance_id` | `EntityId` | resolves |

Adoption cannot mutate a Booking.

### 12.2 `MoneyItem`

| Field | Type | Required | Null |
|---|---|---:|---:|
| `id` | `EntityId` | yes | no |
| `booking_id` | `EntityId` | yes | yes |
| `service_id` | `EntityId` | yes | yes |
| `transfer_template_id` | `EntityId` | yes | yes |
| `category` | `MoneyCategory` | yes | no |
| `payment_state` | `PaymentState` | yes | no |
| `amount_paise` | `NullableMoneyPaise` | yes | yes |
| `provenance_id` | `EntityId` | yes | no |

At least one of booking/service/transfer reference must be non-null unless the item is a scenario-level mandatory fee. `amount_paise=null` is allowed only for `potential_refund`/`potential`; unknown mandatory fees produce an unknown policy check rather than a null due charge.

Valid category/state pairs:

| Category | Allowed state |
|---|---|
| `sunk_cost` | `paid` |
| `received_refund` | `paid` |
| `potential_refund` | `potential` |
| `retained_charge`, `new_purchase`, `mandatory_fee` | `due` |

## 13. Activity-definition contracts

`ActivityDefinition` is a discriminated union on `kind`. Shared fields are `id`, `kind`, `hard`, `booking_id` (nullable) and `provenance_id` (nullable only for a derived processing activity).

### 13.1 `FixedTransportActivityDefinition`

```json
{
  "id": "act:T1",
  "kind": "fixed_transport",
  "hard": true,
  "booking_id": "booking:train-original",
  "provenance_id": "prov:fixture:mumbai-goa-v2",
  "service_id": "svc:T1:2026-09-26"
}
```

`service_id` is required. Transfer/location/window/duration/commitment fields are forbidden.

### 13.2 `FlexibleTransferActivityDefinition`

Requires `transfer_template_id`. Service/location/window/duration/commitment fields are forbidden. Schedule is derived from predecessor readiness and template.

### 13.3 `ProcessingActivityDefinition`

Requires `location_id` and `duration_sec > 0`. It may carry `derived_from_service_id`; when present, its duration must equal that service’s exit allowance and it may be materialized only once in a path.

### 13.4 `HotelCheckinActivityDefinition`

Requires `location_id`, `earliest_start`, `latest_start`, and `duration_sec > 0`. `latest_start >= earliest_start`. Service/transfer/commitment fields are forbidden.

### 13.5 `CommitmentActivityDefinition`

Requires `location_id`, `start_at`, and `readiness_allowance_sec >= 0`. It contains no input `latest_arrival`; the server derives `start_at - readiness_allowance_sec`. Its `hard` flag controls eligibility.

### 13.6 `Dependency`

| Field | Type | Rule |
|---|---|---|
| `id` | `EntityId` | unique |
| `from_id` | `EntityId` | resolves to activity |
| `to_id` | `EntityId` | resolves; differs from `from_id` |
| `buffer_sec` | `DurationSec` | nonnegative; movement not duplicated |
| `reason` | string 1–80 | controlled fixture/domain explanation token |

Dependencies must form a DAG. Stable topological order uses activity ID for ties.

### 13.7 `ItineraryDefinition`

| Field | Type | Rule |
|---|---|---|
| `activities` | `ActivityDefinition[]` | 1–20, unique IDs |
| `dependencies` | `Dependency[]` | 0–80, valid DAG |

## 14. Evaluated activity contracts

Input definitions never accept authoritative computed status or times. Output uses `EvaluatedActivity`:

| Field | Type | Required | Null |
|---|---|---:|---:|
| `activity_id` | `EntityId` | yes | no |
| `kind` | `ActivityKind` | yes | no |
| `service_id` | `EntityId` | yes | yes |
| `transfer_template_id` | `EntityId` | yes | yes |
| `origin_id` | `EntityId` | yes | yes |
| `destination_id` | `EntityId` | yes | yes |
| `start_at` | `AwareDateTime` | yes | yes |
| `end_at` | `AwareDateTime` | yes | yes |
| `ready_at` | `AwareDateTime` | yes | yes |
| `cutoff_at` | `AwareDateTime` | yes | yes |
| `slack_sec` | `SlackSec` | yes | yes |
| `status` | `FeasibilityStatus` | yes | no |
| `reason_codes` | `DomainReasonCode[]` | yes | no |
| `provenance_ids` | `EntityId[]` | yes | no |

Null schedule fields mean blocked/unknown/not-applicable and must be supported by reason codes. `end_at >= start_at` when both are present.

## 15. Versioned effective-service state

### 15.1 `EffectiveServiceState`

| Field | Type | Rule |
|---|---|---|
| `service_id` | `EntityId` | resolves to immutable catalog definition |
| `effective_departure` | `AwareDateTime` | required |
| `effective_arrival` | `AwareDateTime` | strictly after departure |
| `status` | `ServiceStatus` | scheduled/delayed/cancelled |
| `last_event_id` | `EntityId` | null at baseline, otherwise resolves |
| `provenance_id` | `EntityId` | resolves |

At trip creation, every catalog service receives a baseline state with effective times equal scheduled times, status `scheduled` and `last_event_id=null`. Timing events replace effective times and set `delayed` when they differ. Cancellation changes only status/provenance/event reference while retaining the latest effective times. The effective state’s `provenance_id` becomes the nested event provenance ID.

This separation is mandatory: event processing never edits `ServiceCatalog`.

## 16. Constraint contract

### 16.1 `Constraints`

| Field | Type | Rule |
|---|---|---|
| `party_size` | strict integer | exactly 1 |
| `max_cash_required_paise` | `MoneyPaise` | hard limit |
| `max_incremental_cost_paise` | `MoneyPaise` | hard limit |
| `allowed_modes` | `TransportMode[]` | 1–4, unique |
| `required_commitment_ids` | `EntityId[]` | 1–20, unique; resolve to hotel/commitment activities |
| `accessibility_required` | strict boolean | must equal TravelerProfile setting |
| `ranking_preset` | `RankingPreset` | affects ordering only |
| `max_new_fixed_legs` | strict integer | 0–2 |
| `max_transfer_legs` | strict integer | 0–8 |
| `horizon_end` | `AwareDateTime` | after CurrentState `as_of` on normal create/update |
| `risk_threshold_sec` | `DurationSec` | hero 1800; warning heuristic |

Constraint replacement is full, never JSON Merge Patch. Omitting a field is a 422 error, not “keep old value.”

## 17. Evidence-value union

`ConstraintCheck.observed` and `required` use a discriminated `EvidenceValue`, not untyped JSON.

| `value_kind` | `value` type | Optional unit/meaning |
|---|---|---|
| `unknown` | null | required explanation in reason code |
| `timestamp` | `AwareDateTime` | instant |
| `duration_sec` | strict signed integer | `seconds` |
| `money_paise` | `SignedMoneyPaise` | `INR_paise` |
| `integer` | strict integer | optional short unit |
| `boolean` | strict boolean | none |
| `text` | string 0–200 | controlled/non-sensitive text |
| `entity_id` | `EntityId` | entity kind supplied separately if useful |
| `string_list` | string[] | 0–20 unique values |

All variants contain exactly `value_kind`, `value`, and nullable `unit`. Extra fields are forbidden.

## 18. Constraint-check contract

`ConstraintCheck`:

| Field | Type | Rule |
|---|---|---|
| `constraint_id` | `EntityId` | unique within plan/evaluation |
| `passed` | strict boolean or null | null means unknown, never pass |
| `reason_code` | `DomainReasonCode` | exact machine explanation |
| `observed` | `EvidenceValue` | required even if unknown |
| `required` | `EvidenceValue` | required |
| `provenance_ids` | `EntityId[]` | unique, may be empty only for pure derived rule |

Known false takes precedence over null in overall feasibility, but both records remain present.

## 19. Impact contract

`ImpactRecord`:

| Field | Type | Rule |
|---|---|---|
| `activity_id` | `EntityId` | affected activity |
| `root_event_ids` | `EntityId[]` | 1–20, unique |
| `causal_activity_path` | `EntityId[]` | shortest stable path |
| `before_status` | `FeasibilityStatus` | required |
| `after_status` | `FeasibilityStatus` | required |
| `before_ready_at` | `AwareDateTime` | nullable |
| `after_ready_at` | `AwareDateTime` | nullable |
| `cutoff_at` | `AwareDateTime` | nullable |
| `before_slack_sec` | `SlackSec` | nullable |
| `after_slack_sec` | `SlackSec` | nullable |
| `reason_codes` | `DomainReasonCode[]` | nonempty for changed/blocked item |
| `constraint_checks` | `ConstraintCheck[]` | relevant evidence |

## 20. Trip aggregate and view contracts

### 20.1 `TripAggregate`

| Field | Type | Rule |
|---|---|---|
| `schema_version` | literal `resilitrip-api-1.0` | required |
| `id` | `EntityId` | stable trip ID |
| `version` | strict integer ≥1 | monotonically increases |
| `scenario_id` | `EntityId` | nullable for manual trip |
| `mode` | literal `demo` | P0 only |
| `display_timezone` | literal `Asia/Kolkata` | P0 |
| `currency` | literal `INR` | P0 |
| `truth_label` | literal `SYNTHETIC SCENARIO — NOT BOOKABLE` | required in P0 |
| `traveler` | `TravelerProfile` | one traveler |
| `catalog_version` | `EntityId` | immutable catalog reference |
| `decision_allowance_sec` | `DurationSec` | immutable readiness allowance applied after CurrentState `as_of` |
| `current_state` | `CurrentState` | current recovery origin |
| `constraints` | `Constraints` | current hard limits/preset |
| `original_itinerary` | `ItineraryDefinition` | immutable after create |
| `active_itinerary` | `ItineraryDefinition` | original, adopted proposal or guarded remaining-journey edit |
| `bookings` | `Booking[]` | states preserved on adoption |
| `baseline_money_items` | `MoneyItem[]` | immutable baseline context |
| `baseline_remaining_spend_paise` | `MoneyPaise` | reconciles due baseline items |
| `effective_services` | `EffectiveServiceState[]` | one per catalog service |
| `provenance` | `ProvenanceRecord[]` | trip/current-state/constraint/event sources introduced across versions |
| `constraints_provenance_id` | `EntityId` | source of current Constraints; resolves in trip provenance |
| `adopted_plan_id` | `EntityId` | nullable |
| `last_mutation_kind` | `MutationKind` | audit/display aid |

### 20.2 `AvailableActions`

Exact booleans:

```json
{
  "can_apply_event": true,
  "can_edit_constraints": true,
  "can_edit_current_state": true,
  "can_edit_itinerary": true,
  "can_generate_plans": true,
  "can_adopt_plan": false,
  "can_reset": true
}
```

These are convenience projections, not authorization. Mutation endpoints still validate all rules.

### 20.3 `TripViewSnapshot`

| Field | Type | Rule |
|---|---|---|
| `trip` | `TripAggregate` | authoritative aggregate |
| `catalog` | `ServiceCatalog` | exact referenced catalog |
| `evaluated_itinerary` | `EvaluatedActivity[]` | current mode evaluation |
| `overall_status` | `FeasibilityStatus` | current active itinerary |
| `impacts` | `ImpactRecord[]` | empty before any relevant event |
| `provenance` | `ProvenanceRecord[]` | records required for visible fields |
| `available_actions` | `AvailableActions` | current UI hints |

All nested plan/trip/catalog references must match `trip.version` and `trip.catalog_version`.
`TripViewSnapshot.provenance` is the ID-deduplicated visible union of catalog and trip provenance. Two records with the same ID but different canonical content are an integrity error.

## 21. Event request union

Common event fields:

| Field | Type | Rule |
|---|---|---|
| `event_id` | `EntityId` | retry identity unique per trip |
| `source_id` | `EntityId` | replay source identity |
| `source_sequence` | strict integer ≥1 | strictly increases per source for new events |
| `expected_trip_version` | strict integer ≥1 | optimistic concurrency |
| `type` | `EventType` | discriminator |
| `service_id` | `EntityId` | resolves |
| `observed_at` | `AwareDateTime` | source time |
| `effective_at` | `AwareDateTime` | applicability time |
| `provenance` | `ProvenanceRecord` | source introduced by this command; P0 accepts synthetic replay or user-reported kinds |

### 21.1 `ServiceTimingUpdatedCommand`

Adds required `new_departure_at` and `new_arrival_at`; arrival must be strictly later. No delay-minutes field exists.

The nested provenance ID is appended to versioned trip provenance when the event is first applied. Its `observed_at` must equal the command’s `observed_at`. Reusing a provenance ID with different canonical content is a 409 `PROVENANCE_ID_CONFLICT`. An identical event retry does not append it again.

```json
{
  "event_id": "event:D1",
  "source_id": "replay:mumbai-goa-v2",
  "source_sequence": 1,
  "expected_trip_version": 1,
  "type": "SERVICE_TIMING_UPDATED",
  "service_id": "svc:T1:2026-09-26",
  "observed_at": "2026-09-26T05:00:00+05:30",
  "effective_at": "2026-09-26T05:00:00+05:30",
  "new_departure_at": "2026-09-26T09:00:00+05:30",
  "new_arrival_at": "2026-09-26T18:30:00+05:30",
  "provenance": {
    "id": "prov:replay:D1",
    "kind": "synthetic",
    "verification": "fixture",
    "observed_at": "2026-09-26T05:00:00+05:30",
    "retrieved_at": "2026-09-26T05:00:00+05:30",
    "valid_until": null,
    "source_ref": "replay:mumbai-goa-v2"
  }
}
```

### 21.2 `ServiceCancelledCommand`

Contains only common fields. Timing fields are forbidden.

### 21.3 `EventResult`

| Field | Type | Rule |
|---|---|---|
| `disposition` | `EventDisposition` | applied or duplicate |
| `applied` | strict boolean | true only for new applied event |
| `event_id` | `EntityId` | command identity |
| `prior_trip_version` | strict integer | version before original application |
| `current_trip_version` | strict integer | new/current version |
| `snapshot` | `TripViewSnapshot` | current authoritative state |

An identical retry returns 200 with `duplicate`, `applied=false` and no new version. Changed payload under an existing event ID returns 409 `EVENT_ID_CONFLICT`.

## 22. Plan contracts

### 22.1 `PlanObjectiveValues`

| Field | Type |
|---|---|
| `cash_required_paise` | `MoneyPaise` |
| `final_required_arrival_at` | `AwareDateTime` |
| `changed_original_booking_count` | strict integer 0–50 |

### 22.2 `PlanEvaluation`

| Field | Type | Rule |
|---|---|---|
| `id` | `EntityId` | server-generated stable plan ID |
| `trip_id` | `EntityId` | exact owner |
| `trip_version` | strict integer ≥1 | generation version |
| `catalog_version` | `EntityId` | generation catalog |
| `run_id` | `EntityId` or null | present in planner-result context; null for direct plan lookup |
| `lifecycle_status` | `PlanLifecycleStatus` | preview/adopted/stale |
| `evaluation_status` | `FeasibilityStatus` | hard result |
| `valid_until` | `AwareDateTime` | exclusive adoption boundary |
| `sequence_ids` | `EntityId[]` | 1–20 ordered service/transfer/obligation IDs |
| `sequence_signature` | string | 64 lowercase hexadecimal SHA-256 characters over the canonical version/catalog/sequence tuple |
| `proposed_itinerary` | `ItineraryDefinition` | complete adoptable definition generated by server |
| `activity_sequence` | `EvaluatedActivity[]` | 1–20 complete ordered remaining activities |
| `service_ids` | `EntityId[]` | stable order, unique |
| `transfer_template_ids` | `EntityId[]` | stable order, unique |
| `money_items` | `MoneyItem[]` | unique and reconciled |
| `cash_required_paise` | `MoneyPaise` | server computed |
| `incremental_cost_paise` | `SignedMoneyPaise` | server computed |
| `potential_refund_paise` | `NullableMoneyPaise` | hero null; excluded from cash |
| `final_required_arrival_at` | `AwareDateTime` | venue arrival for hero |
| `event_slack_sec` | `SlackSec` | final hard commitment slack |
| `changed_original_booking_ids` | `EntityId[]` | unique |
| `constraint_checks` | `ConstraintCheck[]` | full structured evidence |
| `provenance_ids` | `EntityId[]` | visible sources |
| `objective_values` | `PlanObjectiveValues` | exact frontier tuple inputs |
| `frontier_member` | strict boolean | true only if feasible nondominated |
| `display_rank` | strict integer ≥1 or null | set for displayed plans in this run |
| `ranking_reason_code` | `RankingReasonCode` or null | current preset explanation |
| `simulated` | literal `true` | mandatory |
| `bookable` | literal `false` | mandatory |
| `reason_codes` | `DomainReasonCode[]` | summary; details remain in checks |

Client requests never contain `PlanEvaluation`.

The immutable plan record is unique by `(trip_id, id, trip_version, catalog_version)` and sequence signature. Planner-run membership stores result bucket, current preset display rank and ranking reason separately. Regenerating the same sequence under another preset reuses the plan evaluation and creates another run-membership record; it does not clone or overwrite the plan. In a direct plan lookup, `run_id`, `display_rank`, and `ranking_reason_code` are null because rank has meaning only inside a specific run/preset.

### 22.3 `SearchScope`

| Field | Type |
|---|---|
| `catalog_version` | `EntityId` |
| `replay_as_of` | `AwareDateTime` |
| `horizon_end` | `AwareDateTime` |
| `max_catalog_services` | strict integer 0–50 |
| `max_new_fixed_legs` | strict integer 0–2 |
| `max_transfer_legs` | strict integer 0–8 |
| `max_activities` | literal `20` |

### 22.4 `PlannerCounts`

Exact nonnegative integers:

- `states_expanded`;
- `complete_paths`;
- `duplicate_paths`;
- `feasible_total`;
- `uncertain_total`;
- `rejected_total`;
- `frontier_total`;
- `displayed_total`;
- `pruned_by_reason`, a map whose keys are `DomainReasonCode` and values are nonnegative integers.

The reason-count map is the only dynamic map in planner output.

### 22.5 `PlannerResult`

| Field | Type | Rule |
|---|---|---|
| `run_id` | `EntityId` | unique run |
| `trip_id` | `EntityId` | owner |
| `trip_version` | strict integer ≥1 | input version |
| `catalog_version` | `EntityId` | input catalog |
| `ranking_preset` | `RankingPreset` | applied tuple |
| `result_status` | `PlannerResultStatus` | exact state |
| `search_complete` | strict boolean | bounded-space exhaustion |
| `interruption_reason` | `DomainReasonCode` | nullable; `SEARCH_INCOMPLETE` for partial |
| `scope` | `SearchScope` | limits behind claims |
| `counts` | `PlannerCounts` | reconciliation fields |
| `runtime_ms` | nonnegative finite number | measurement only, not deterministic result |
| `feasible_plans` | `PlanEvaluation[]` | only feasible/at-risk frontier, max 3 displayed |
| `uncertain_plans` | `PlanEvaluation[]` | max 10 representative complete options |
| `rejected_plans` | `PlanEvaluation[]` | max 10 representative options |

Reconciliation rules:

- `displayed_total == len(feasible_plans)`;
- every feasible plan is `frontier_member=true` and status feasible/at-risk;
- `no_feasible_catalog_plan` requires `search_complete=true` and `feasible_total=0`;
- `needs_input` requires required unknown evidence or unsupported current state;
- `partial_search` requires `search_complete=false` and adoption disabled;
- `runtime_ms` is excluded from canonical deterministic equality.

## 23. Provider action and adoption contracts

### 23.1 `ProviderAction`

| Field | Type | Rule |
|---|---|---|
| `id` | `EntityId` | unique in checklist |
| `title` | `DisplayLabel` | imperative verification step |
| `provider_key` | enum `indian_rail_enquiry`, `airline_or_ota`, `hotel`, `local_transfer` | allowlist lookup only |
| `status` | `ProviderActionStatus` | never provider-confirmed in P0 |
| `required_before_external_change` | strict boolean | guidance |
| `reason` | string 1–240 | deterministic, non-legal wording |
| `handoff_available` | strict boolean | whether configured browser link exists |

No request accepts an arbitrary URL. The browser maps `provider_key` to server/config-approved destinations.

### 23.2 `AdoptionRecord`

| Field | Type | Rule |
|---|---|---|
| `id` | `EntityId` | immutable audit ID |
| `trip_id` | `EntityId` | owner |
| `plan_id` | `EntityId` | adopted server plan |
| `prior_trip_version` | strict integer ≥1 | before adoption |
| `resulting_trip_version` | strict integer ≥2 | exactly prior + 1 |
| `catalog_version` | `EntityId` | matches plan/trip |
| `adopted_at` | `AwareDateTime` | replay/domain adoption time |
| `acknowledge_simulation` | literal `true` | required |
| `external_booking_executed` | literal `false` | mandatory truth |

## 24. Scenario contracts

### 24.1 `ScenarioSummary`

| Field | Type |
|---|---|
| `id` | `EntityId` |
| `name` | `DisplayLabel` |
| `catalog_version` | `EntityId` |
| `display_timezone` | string |
| `currency` | literal `INR` |
| `truth_label` | required P0 literal |
| `available` | strict boolean |

### 24.2 Executable scenario fixture

`InstalledScenarioDefinition` contains exactly:

- `id: EntityId`;
- `name: DisplayLabel`;
- `mode: "demo"`;
- `display_timezone: "Asia/Kolkata"`;
- `currency: "INR"`;
- `truth_label: "SYNTHETIC SCENARIO — NOT BOOKABLE"`;
- `replay_start: AwareDateTime`;
- `decision_allowance_sec: DurationSec`;
- `max_activities: 20`;
- `max_catalog_services: 50`; and
- `max_displayed_frontier_plans: 3`.

The executable file `data/fixtures/mumbai-goa-v2.json` validates as `ExecutableScenarioFixture` with exactly:

| Field | Type |
|---|---|
| `schema_version` | literal `resilitrip-api-1.0` |
| `scenario` | `InstalledScenarioDefinition` |
| `catalog` | `ServiceCatalog` |
| `traveler` | `TravelerProfile` |
| `current_state` | `CurrentState` |
| `constraints` | `Constraints` |
| `original_itinerary` | `ItineraryDefinition` |
| `bookings` | `Booking[]` |
| `baseline_money_items` | `MoneyItem[]` |
| `trip_provenance` | `ProvenanceRecord[]` for initial current state and constraints |
| `constraints_provenance_id` | `EntityId` resolving in `trip_provenance` |
| `replay_events` | event-command union array, 0–20 |

It contains no `expected_outcomes`. Golden results live under tests and are never supplied to application planning code.

### 24.3 `FixtureTripCreate`

```json
{
  "source_type": "fixture",
  "scenario_id": "mumbai-goa-v2",
  "display_name": "Asha"
}
```

`display_name` is nullable and overrides only the fictional display alias. It does not alter financial/planning facts.

### 24.4 `ManualTripCreate`

Discriminator `source_type="manual"`; exact fields:

- `display_timezone` (P0 literal `Asia/Kolkata`);
- `decision_allowance_sec: DurationSec`;
- `traveler: TravelerProfile`;
- `catalog: ServiceCatalog` with `scenario_id=null`;
- `current_state: CurrentState`;
- `constraints: Constraints`;
- `original_itinerary: ItineraryDefinition`;
- `bookings: Booking[]`;
- `baseline_money_items: MoneyItem[]`;
- `trip_provenance: ProvenanceRecord[]`; and
- `constraints_provenance_id: EntityId` resolving in `trip_provenance`.

The server generates trip ID, effective-service baseline and baseline remaining-spend reconciliation. A manual request cannot include expected outcomes, plans, impacts, effective-service overrides or adopted-plan state.

## 25. Mutation commands

### 25.1 `ConstraintsReplaceCommand`

```json
{
  "expected_trip_version": 2,
  "constraints": {
    "party_size": 1,
    "max_cash_required_paise": 700000,
    "max_incremental_cost_paise": 900000,
    "allowed_modes": ["rail", "air", "road_transfer"],
    "required_commitment_ids": ["act:H1", "act:E1"],
    "accessibility_required": false,
    "ranking_preset": "cheapest",
    "max_new_fixed_legs": 2,
    "max_transfer_legs": 8,
    "horizon_end": "2026-09-27T05:00:00+05:30",
    "risk_threshold_sec": 1800
  },
  "provenance": {
    "id": "prov:user:budget-v3",
    "kind": "user_reported",
    "verification": "unverified",
    "observed_at": "2026-09-26T05:02:00+05:30",
    "retrieved_at": "2026-09-26T05:02:00+05:30",
    "valid_until": null,
    "source_ref": "user-action:budget-edit"
  }
}
```

### 25.2 `CurrentStateReplaceCommand`

Contains exactly `expected_trip_version`, full `current_state`, and a new `provenance: ProvenanceRecord`. The provenance ID must equal `current_state.provenance_id`; its P0 kind is `user_reported` or `synthetic`. Updating only `as_of` still creates a new trip version and stales previews.

`ConstraintsReplaceCommand.provenance` is likewise required; on success its ID becomes `TripAggregate.constraints_provenance_id`. Provenance-ID reuse with different canonical content is a conflict.

### 25.3 `ItineraryEditCommand`

Contains exactly:

- `expected_trip_version`;
- `active_itinerary`;
- `constraints`;
- `acknowledge_hard_changes`; and
- `provenance`.

This is a full-replacement command, not patch semantics. It replaces the active itinerary and resulting constraints atomically. It cannot change the original itinerary, catalog service definitions, effective-service state, Bookings, completed activities or the current activity. Removing a hard activity requires literal `acknowledge_hard_changes=true`; acknowledgement does not make an otherwise invalid itinerary acceptable. The replacement must retain a valid dependency DAG and an order compatible with `constraints.required_commitment_ids`. On success, the provenance ID becomes `TripAggregate.constraints_provenance_id`.

### 25.4 `PlannerCommand`

```json
{
  "expected_trip_version": 2,
  "expected_catalog_version": "catalog:mumbai-goa-v2",
  "ranking_preset": "cheapest"
}
```

Search limits come from current constraints/server constants, not arbitrary request overrides. Plan generation does not change trip version.

### 25.5 `AdoptionCommand`

```json
{
  "expected_trip_version": 2,
  "plan_id": "plan:F3:v2",
  "acknowledge_simulation": true
}
```

No plan object, amount, status or sequence is accepted.

### 25.6 `ResetCommand`

```json
{
  "expected_trip_version": 3,
  "scenario_id": "mumbai-goa-v2"
}
```

Scenario ID must match the trip’s approved fixture origin in P0. Reset returns baseline content under version 4, not version 1.

The reset endpoint supports installed-fixture trips only. A manual trip has `scenario_id=null` and returns 409 `RESET_NOT_SUPPORTED` without mutation; the user may create a new manual trip instead.

## 26. Response models

### 26.1 `TripCreatedResponse`

Fields: `trip_id`, `trip_version`, `catalog_version`, `snapshot`. Status 201.

### 26.2 `TripSnapshotResponse`

Fields: `snapshot`. Status 200.

### 26.3 `MutationResponse`

Fields: `mutation_kind`, `changed` (strict boolean), `prior_trip_version`, `current_trip_version`, `staled_plan_count`, `snapshot`. Status 200.

An identical full constraints/current-state replacement or identical canonical active-itinerary-plus-constraints replacement returns `changed=false`, equal prior/current versions and zero newly staled plans. A genuine replacement and every reset return `changed=true`; reset increments even when restored content equals the original baseline by design.

### 26.4 `PlannerResponse`

Fields: `planner_result`, `snapshot_version`, `catalog_version`. It does not repeat a full trip snapshot; the version pair must equal the UI’s current snapshot. Status 200.

### 26.5 `AdoptionResponse`

Fields: `adoption`, `provider_actions`, `snapshot`. Status 200.

### 26.6 `EventResponse`

Fields: `event_result`. Status 200.

### 26.7 `DeleteResponse`

P0 has no browser delete endpoint. It stores fictional local data and provides reset. A controlled development command may remove a named demo trip. Any future real-user mode must add authenticated deletion/retention contracts before collecting data.

This deliberately supersedes the provisional `DELETE /api/trips/{id}` row in the research dossier. Deletion was not a locked PRD P0 capability, while an unauthenticated destructive browser route adds avoidable demo risk. The scope documents’ reset requirement remains fully implemented.

### 26.8 Health responses

`LiveHealthResponse` contains exactly `status="ok"`, `service="resilitrip"`, and `contract_version="resilitrip-api-1.0"`.

`ReadyHealthResponse` contains those fields plus `database="ok"`, `schema_revision` as a 1–64 character migration ID, and nonnegative `installed_scenario_count`. An unhealthy readiness check returns 503 `ProblemResponse`; it does not serialize `status="ok"` with a broken dependency.

## 27. Endpoint catalogue

| Method and path | Operation ID | Request | Success | Mutates trip? |
|---|---|---|---|---:|
| `GET /api/health/live` | `health_live` | none | 200 plain JSON status | no |
| `GET /api/health/ready` | `health_ready` | none | 200 or 503 | no |
| `GET /api/v1/scenarios` | `list_scenarios` | none | 200 `ScenarioSummary[]` | no |
| `POST /api/v1/trips` | `create_trip` | `FixtureTripCreate \| ManualTripCreate` | 201 `TripCreatedResponse` | creates v1 |
| `GET /api/v1/trips/{trip_id}` | `get_trip` | path ID | 200 `TripSnapshotResponse` | no |
| `PUT /api/v1/trips/{trip_id}/constraints` | `replace_constraints` | `ConstraintsReplaceCommand` | 200 `MutationResponse` | yes |
| `PUT /api/v1/trips/{trip_id}/current-state` | `replace_current_state` | `CurrentStateReplaceCommand` | 200 `MutationResponse` | yes |
| `PUT /api/v1/trips/{trip_id}/itinerary` | `replace_active_itinerary` | `ItineraryEditCommand` | 200 `MutationResponse` | yes |
| `POST /api/v1/trips/{trip_id}/events` | `apply_event` | event union | 200 `EventResponse` | only applied |
| `POST /api/v1/trips/{trip_id}/plans` | `generate_plans` | `PlannerCommand` | 200 `PlannerResponse` | no |
| `GET /api/v1/trips/{trip_id}/plans/{plan_id}` | `get_plan` | path IDs | 200 `PlanEvaluation` | no |
| `POST /api/v1/trips/{trip_id}/adoptions` | `adopt_plan` | `AdoptionCommand` | 200 `AdoptionResponse` | yes |
| `POST /api/v1/trips/{trip_id}/reset` | `reset_trip` | `ResetCommand` | 200 `MutationResponse` | yes |

Unknown routes return 404. OPTIONS behavior is framework/CORS infrastructure and not part of the application contract.

## 28. Endpoint semantics

### 28.1 List scenarios

Returns only approved locally installed fixtures. It does not scan user paths or remote registries. `mumbai-goa-v2` must be available in the canonical demo build.

### 28.2 Create trip

Processing order:

1. request size and JSON syntax;
2. discriminator/schema validation;
3. field and cross-reference validation;
4. DAG/current-state/baseline reconciliation;
5. catalog insertion/reuse by exact canonical hash;
6. trip v1 transaction;
7. current baseline evaluation;
8. response projection.

If an existing immutable catalog version has a different hash, return 409 `CATALOG_VERSION_CONFLICT`.

### 28.3 Replace constraints/current state

Require the current expected version. Create one new trip version, preserve original itinerary/bookings/baseline, mark preview plans stale, recalculate active impact, and return one snapshot.

After the version check, compare canonical replacement content. Identical constraints or CurrentState are successful no-ops as defined in §26.3; they do not create audit/version noise.

### 28.4 Guarded remaining-journey edit

Require the current expected version and a full active-itinerary/constraints replacement. A material edit updates both values atomically, increments the trip version exactly once and stales all previews. Identical canonical active itinerary plus constraints is a successful no-op even when the submitted provenance is new. The command cannot mutate the original itinerary, catalog, effective-service state, Bookings, completed prefix or current activity. Hard-activity removal requires literal acknowledgement. The resulting dependency graph must be a valid DAG, and its reachability must preserve the declared required-commitment order.

### 28.5 Apply event

Use Document 05’s duplicate-before-version order. Invalid/unsupported events return no snapshot mutation. Successful new event increments version once. Duplicate returns the current snapshot even if its version is now later than the event’s originally applied version.

### 28.6 Generate plans

If computation completes but trip/catalog changes before save, return 409 `VERSION_CONFLICT`/`CATALOG_VERSION_CONFLICT` and persist no current preview. Result sets follow §22. Search `error` is normally transported as `ProblemResponse`; the enum remains available for stored diagnostics/UI exhaustiveness.

### 28.7 Get plan

The trip ID must own the plan. A stale plan may be read for explanation and returns `lifecycle_status=stale`; it cannot be adopted.

### 28.8 Adopt plan

Revalidate acknowledgement, ownership, versions, catalog, lifecycle, complete search, exclusive time validity, signature, totals and all hard checks within one write transaction. On success, return adopted plan state, proposed active itinerary, unchanged Bookings, external false and provider actions.

### 28.9 Reset

Restore canonical baseline contents and replay time under version `current + 1`; mark all prior previews stale. It never reuses an old plan as current.

## 29. Planner response example

This example intentionally shows the decisive fields and valid nesting; arrays abbreviated with comments are documentation-only and are not literal JSON fixtures.

```jsonc
{
  "planner_result": {
    "run_id": "run:22222222-2222-4222-8222-222222222222",
    "trip_id": "trip:11111111-1111-4111-8111-111111111111",
    "trip_version": 2,
    "catalog_version": "catalog:mumbai-goa-v2",
    "ranking_preset": "cheapest",
    "result_status": "complete",
    "search_complete": true,
    "interruption_reason": null,
    "scope": {
      "catalog_version": "catalog:mumbai-goa-v2",
      "replay_as_of": "2026-09-26T05:00:00+05:30",
      "horizon_end": "2026-09-27T05:00:00+05:30",
      "max_catalog_services": 50,
      "max_new_fixed_legs": 2,
      "max_transfer_legs": 8,
      "max_activities": 20
    },
    "counts": {
      "states_expanded": 0,
      "complete_paths": 4,
      "duplicate_paths": 0,
      "feasible_total": 2,
      "uncertain_total": 0,
      "rejected_total": 2,
      "frontier_total": 2,
      "displayed_total": 2,
      "pruned_by_reason": {}
    },
    "runtime_ms": 0.0,
    "feasible_plans": [
      {
        "id": "plan:F3:v2",
        "trip_id": "trip:11111111-1111-4111-8111-111111111111",
        "trip_version": 2,
        "catalog_version": "catalog:mumbai-goa-v2",
        "run_id": "run:22222222-2222-4222-8222-222222222222",
        "lifecycle_status": "preview",
        "evaluation_status": "feasible",
        "valid_until": "2026-09-26T05:15:00+05:30",
        "sequence_ids": ["xfer:X1", "svc:F3:2026-09-26", "process:F3-exit", "xfer:X-GOI-HOTEL", "act:H1", "xfer:C2", "act:E1"],
        "sequence_signature": "fc6101d0ac516bb977c836b24e8414d51beb52ab25a969a524f70ce97206c1df",
        "proposed_itinerary": {"activities": [], "dependencies": []},
        "activity_sequence": [],
        "service_ids": ["svc:F3:2026-09-26"],
        "transfer_template_ids": ["xfer:X1", "xfer:X-GOI-HOTEL", "xfer:C2"],
        "money_items": [],
        "cash_required_paise": 650000,
        "incremental_cost_paise": 520000,
        "potential_refund_paise": null,
        "final_required_arrival_at": "2026-09-26T17:20:00+05:30",
        "event_slack_sec": 6900,
        "changed_original_booking_ids": ["booking:train-original", "booking:cab-C1"],
        "constraint_checks": [],
        "provenance_ids": ["prov:fixture:mumbai-goa-v2"],
        "objective_values": {
          "cash_required_paise": 650000,
          "final_required_arrival_at": "2026-09-26T17:20:00+05:30",
          "changed_original_booking_count": 2
        },
        "frontier_member": true,
        "display_rank": 1,
        "ranking_reason_code": "LOWEST_CASH_ON_FRONTIER",
        "simulated": true,
        "bookable": false,
        "reason_codes": ["HARD_CONSTRAINTS_PASS"]
      }
    ],
    "uncertain_plans": [],
    "rejected_plans": []
  },
  "snapshot_version": 2,
  "catalog_version": "catalog:mumbai-goa-v2"
}
```

`states_expanded`, `runtime_ms`, full proposed/evaluated activities, money items, checks and rejected plans above are placeholders/abbreviations, not golden expected values. In particular, the empty itinerary is not schema-valid; it is shortened here to avoid duplicating the fixture. The executable golden response generated in Test Strategy must contain actual computed records and must not use empty required evidence arrays. JSONC never enters the runtime fixture.

## 30. Adoption response truth example

```json
{
  "adoption": {
    "id": "adoption:33333333-3333-4333-8333-333333333333",
    "trip_id": "trip:11111111-1111-4111-8111-111111111111",
    "plan_id": "plan:F3:v2",
    "prior_trip_version": 2,
    "resulting_trip_version": 3,
    "catalog_version": "catalog:mumbai-goa-v2",
    "adopted_at": "2026-09-26T05:05:00+05:30",
    "acknowledge_simulation": true,
    "external_booking_executed": false
  },
  "provider_actions": [
    {
      "id": "provider-action:F3-availability",
      "title": "Verify the selected flight and fare",
      "provider_key": "airline_or_ota",
      "status": "not_started",
      "required_before_external_change": true,
      "reason": "ResiliTrip used a synthetic option and did not reserve a seat.",
      "handoff_available": true
    }
  ],
  "snapshot": {}
}
```

The empty snapshot above is documentation shorthand only. Runtime `AdoptionResponse.snapshot` must be a complete `TripViewSnapshot`.

## 31. Problem response

### 31.1 `FieldError`

| Field | Type | Rule |
|---|---|---|
| `path` | string | JSON-pointer style, e.g. `/constraints/max_cash_required_paise` |
| `code` | `ApiErrorCode` | stable machine code |
| `message` | string 1–240 | safe actionable message |
| `rejected_value` | `EvidenceValue` | nullable; omit sensitive/free-text raw values |

### 31.2 `ProblemDetail`

| Field | Type | Rule |
|---|---|---|
| `code` | `ApiErrorCode` | stable |
| `message` | string 1–240 | safe summary |
| `request_id` | string | correlation only |
| `retryable` | strict boolean | client guidance |
| `field_errors` | `FieldError[]` | empty unless field-specific |
| `current_trip_version` | strict integer | nullable; present for trip-version conflict |
| `current_catalog_version` | `EntityId` | nullable; present for catalog conflict |

`ProblemResponse` contains exactly `{ "error": ProblemDetail }`.

Example:

```json
{
  "error": {
    "code": "VERSION_CONFLICT",
    "message": "The trip changed after this screen was loaded. Refresh and try again.",
    "request_id": "req_01K4EXAMPLE",
    "retryable": true,
    "field_errors": [],
    "current_trip_version": 3,
    "current_catalog_version": "catalog:mumbai-goa-v2"
  }
}
```

## 32. HTTP status mapping

| Status | Use | Example codes |
|---:|---|---|
| 200 | Successful read/mutation/result, duplicate event, no-plan/needs-input/partial planner result | domain result body |
| 201 | Trip created | — |
| 400 | Valid JSON but invalid top-level protocol usage not represented by schema | `INVALID_REQUEST` |
| 404 | Trip, scenario or plan not found/owned by path trip | `TRIP_NOT_FOUND`, `SCENARIO_NOT_FOUND`, `PLAN_NOT_FOUND` |
| 409 | Version, ID, catalog, sequence, lifecycle or validity conflict | domain conflict codes |
| 413 | Request bytes exceed limit | `REQUEST_TOO_LARGE` |
| 415 | Wrong media type | `UNSUPPORTED_MEDIA_TYPE` |
| 422 | JSON/schema/field/cross-reference/domain input validation failure | validation codes |
| 500 | Unexpected internal error | `INTERNAL_ERROR` |
| 503 | Database/startup/readiness unavailable | `SERVICE_UNAVAILABLE` |

No-plan is never 404/409/500. Unknown capacity is a planner result/check, not an HTTP validation error when null is allowed.

## 33. Domain conflict mapping

| Code | HTTP | Retryable | Required context |
|---|---:|---:|---|
| `DUPLICATE_EVENT` | 200 | no | disposition duplicate, current snapshot |
| `EVENT_ID_CONFLICT` | 409 | no | existing event identity only; do not echo payload |
| `EVENT_SEQUENCE_STALE` | 409 | no | latest accepted sequence may be included as integer evidence |
| `VERSION_CONFLICT` | 409 | yes | current trip version |
| `CATALOG_VERSION_CONFLICT` | 409 | yes | current catalog version |
| `PROVENANCE_ID_CONFLICT` | 409 | no | existing provenance identity only; do not echo source payload |
| `STALE_PLAN` | 409 | yes | current trip/catalog version and safe reason |
| `PLAN_EXPIRED` | 409 | yes | exclusive valid-until and replay time evidence |
| `PLAN_NOT_ADOPTABLE` | 409 | no | lifecycle/evaluation/search-complete reason |
| `RESET_NOT_SUPPORTED` | 409 | no | manual/non-fixture trip has no installed reset source |
| `ITINERARY_EDIT_INVALID` | 422 | no | safe validation reason and field path when applicable |
| `COMPLETED_ACTIVITY_IMMUTABLE` | 409 | no | completed-prefix conflict only |
| `ACTIVE_ACTIVITY_IMMUTABLE` | 409 | no | current-activity conflict only |
| `HARD_CHANGE_ACKNOWLEDGEMENT_REQUIRED` | 409 | no | hard removal requires literal acknowledgement |

`DUPLICATE_EVENT` remains both a domain reason code and a successful disposition. It does not use `ProblemResponse`.

## 34. API error-code catalogue

In addition to Document 03 reason codes, `ApiErrorCode` includes:

| Code | Meaning |
|---|---|
| `INVALID_JSON` | Body could not be parsed as JSON |
| `INVALID_REQUEST` | Top-level protocol usage invalid |
| `VALIDATION_ERROR` | One or more schema/domain fields invalid |
| `UNKNOWN_FIELD` | Strict model received an unsupported property |
| `MISSING_FIELD` | Required property absent |
| `INVALID_DISCRIMINATOR` | Union discriminator absent/unsupported |
| `INVALID_TIMEZONE` | Timestamp is naive/invalid |
| `INVALID_MONEY` | Money is non-integer/boolean/out of bounds |
| `DUPLICATE_ID` | IDs duplicate inside one aggregate |
| `REFERENCE_NOT_FOUND` | Cross-reference unresolved |
| `INVALID_DEPENDENCY_GRAPH` | Endpoint/cycle rule fails |
| `INVALID_CURRENT_STATE` | CurrentState cross-field rule fails |
| `BASELINE_RECONCILIATION_FAILED` | Remaining baseline does not equal qualifying items |
| `TRIP_NOT_FOUND` | Trip absent |
| `SCENARIO_NOT_FOUND` | Fixture absent |
| `PLAN_NOT_FOUND` | Plan absent or owned by another trip path |
| `CATALOG_VERSION_CONFLICT` | Immutable version hash/current expectation differs |
| `PROVENANCE_ID_CONFLICT` | Existing provenance ID was reused with different canonical content |
| `PLAN_EXPIRED` | Replay time is at/after exclusive cutoff |
| `PLAN_NOT_ADOPTABLE` | Status/search/evaluation prevents adoption |
| `RESET_NOT_SUPPORTED` | Trip has no installed fixture baseline |
| `SIMULATION_ACKNOWLEDGEMENT_REQUIRED` | Adoption acknowledgement is not literal true |
| `REQUEST_TOO_LARGE` | Body exceeds 262,144 bytes |
| `UNSUPPORTED_MEDIA_TYPE` | Non-JSON request |
| `INTERNAL_DATA_INTEGRITY_ERROR` | Stored canonical hash/model invalid |
| `INTERNAL_ERROR` | Unexpected server error |
| `SERVICE_UNAVAILABLE` | Readiness/database unavailable |
| `ITINERARY_EDIT_INVALID` | Replacement itinerary, constraints, dependency DAG or commitment order is invalid |
| `COMPLETED_ACTIVITY_IMMUTABLE` | Edit attempted to alter the completed activity prefix |
| `ACTIVE_ACTIVITY_IMMUTABLE` | Edit attempted to alter the current active activity/service |
| `HARD_CHANGE_ACKNOWLEDGEMENT_REQUIRED` | A hard activity was removed without literal acknowledgement |

The OpenAPI schema exposes this closed enum. UI copy maps codes; it never parses English messages to decide behavior.

## 35. Validation error normalization

FastAPI/Pydantic native validation errors must be normalized into `ProblemResponse`; raw framework error arrays are not part of the contract.

Path conversion example:

```text
Pydantic loc: ("body", "constraints", "max_cash_required_paise")
API path:     /constraints/max_cash_required_paise
```

Do not expose Python class names, stack traces, database paths or SQL.

## 36. Version and stale-state matrix

| Change | Trip version | Catalog version | Existing previews |
|---|---:|---:|---|
| Create fixture/manual trip | starts 1 | fixed referenced version | none |
| Generate plans/change preset only | unchanged | unchanged | new run; prior same-version plans may remain readable |
| Accepted service event | +1 | unchanged | stale |
| Identical duplicate event | unchanged | unchanged | unchanged except already-stale state |
| Replace constraints with different canonical content | +1 | unchanged | stale |
| Replace current state/replay time with different canonical content | +1 | unchanged | stale |
| Identical constraints/current-state replacement | unchanged | unchanged | unchanged |
| Material active-itinerary/constraints replacement | +1 | unchanged | stale |
| Identical active-itinerary plus constraints replacement | unchanged | unchanged | unchanged |
| Adopt plan | +1 | unchanged | selected adopted; other previews stale |
| Reset | +1 | restored fixture catalog | all prior stale |
| Catalog record change | new immutable catalog version | new ID | cannot mutate an existing trip silently |

Plan validity is exclusive: `replay_as_of < valid_until` is required.

## 37. Canonical JSON and event equality

Canonicalization used for event retry equality and snapshot hashes:

1. validate into the exact model;
2. exclude transport-only `X-Request-ID` and response metadata;
3. include all domain request fields, including `expected_trip_version` for audit but compare event-domain equality using the originally accepted expected version;
4. serialize enum values as strings and datetimes as canonical offset strings;
5. sort object keys recursively;
6. preserve semantically ordered arrays;
7. use UTF-8, no insignificant whitespace and no ASCII escaping requirement;
8. hash canonical bytes using SHA-256.

For identical event retry, compare the full validated event command to the recorded original accepted command. Do not compare a newly supplied expected version after an event has already applied; the retry must resend the original command unchanged.

Plan sequence signature bytes are defined exactly as UTF-8 encoding of:

```text
{trip_version}|{catalog_version}|{sequence_id_1}|...|{sequence_id_n}
```

The stored/transported value is the lowercase hexadecimal SHA-256 digest. For the F3 example tuple in §29, this produces `fc6101d0ac516bb977c836b24e8414d51beb52ab25a969a524f70ce97206c1df`.

## 38. Document 04 fixture migration

Document 04’s `fixture-spec-1.0` block is a logical source. The executable `mumbai-goa-v2.json` must be transformed to `resilitrip-api-1.0` as follows:

| Logical field/shape | Final contract shape |
|---|---|
| `scenario.catalog_version` | `ServiceCatalog.catalog_version` |
| `scenario` constants | installed scenario metadata plus Trip/Constraints fields |
| service scheduled fields | `ServiceDefinition` in immutable catalog |
| service effective fields/status | baseline `EffectiveServiceState[]` in trip v1 |
| top-level logical `provenance` list | split into immutable catalog provenance, initial trip provenance, and nested replay-event provenance |
| single record `provenance_id` | default provenance plus empty/explicit `field_provenance` overrides |
| policy-specific optional fields | `policy_kind` discriminated policy union |
| activity `planned_start/planned_end` | removed from definitions; server produces `EvaluatedActivity` |
| commitment `latest_arrival` | removed from input; derived from start/readiness allowance |
| scenario `decision_allowance_sec` | immutable `TripAggregate.decision_allowance_sec` and installed-scenario field |
| scenario `search_horizon_end` | `Constraints.horizon_end` |
| location `lat`/`lon` | `latitude`/`longitude` |
| booking/activity records without provenance | explicit fixture-default `provenance_id` |
| `original_activities` and `original_dependencies` | `original_itinerary.activities` and `.dependencies` |
| baseline money items | TripAggregate baseline items |
| event D1 | replay control/example command, not auto-applied at creation |
| `expected_outcomes` | test-only golden file, never accepted by API or planner |
| per-plan `valid_until` | `PlanEvaluation.valid_until`, still exclusive |
| `plan_valid_until_inclusive=false` | removed as redundant; exclusivity is fixed by the contract |

Nested expected-outcome keys such as `after_D1`, `venue_arrival`, `hotel_start`, `rank_fastest`, `rank_cheapest`, and `potential_train_refund_paise` remain only in test golden data. Tests compare them with `TripViewSnapshot`, `PlanEvaluation` and ranking outputs; the application never reads them as inputs.

The migration must preserve all Document 04 arithmetic. The logical manifest is not edited in place solely to resemble API output; the executable fixture and golden expected file are separate generated/validated assets.

## 39. OpenAPI requirements

### 39.1 Stable schema names

All models named in this document must have stable OpenAPI component names. Union discriminators must appear in OpenAPI for:

- create-trip source;
- ActivityDefinition;
- PolicyRecord;
- DomainEvent command;
- EvidenceValue.

### 39.2 Stable operation IDs

Use the exact operation IDs in §27. Duplicate or framework-generated path-derived operation IDs fail the contract test.

### 39.3 Examples

OpenAPI embeds:

- fixture creation;
- D1 timing event;
- service cancellation;
- ₹7,000 constraint replacement;
- hero planner command;
- F3 adoption;
- version conflict;
- field validation error.

Examples must validate against their schemas. Documentation shorthand examples in §§29–30 are not exported.

### 39.4 Response declaration

Every endpoint explicitly declares success plus applicable 404/409/413/415/422/500/503 `ProblemResponse` responses. No implicit `any` response body is accepted.

## 40. TypeScript generation

The backend exports deterministic OpenAPI:

```text
python -m resilitrip.tools.export_openapi --output contracts/openapi.json
```

The frontend generates types only:

```text
npx openapi-typescript contracts/openapi.json \
  --output apps/web/src/api/schema.d.ts
```

`openapi-typescript` is a locked development dependency. The frontend maintains a small reviewed `fetch` client rather than adopting a second runtime client framework.

CI/local contract check:

1. export OpenAPI;
2. generate TypeScript;
3. fail if committed files differ;
4. run TypeScript compilation;
5. validate canonical examples against OpenAPI;
6. run backend response-model serialization tests.

Frontend code imports generated operation/schema types. Handwritten duplicates of `PlanEvaluation`, `TripViewSnapshot`, enums or problem responses are prohibited.

## 41. Frontend runtime guards

Static TypeScript does not validate network bytes. The P0 client performs small boundary checks before replacing the current snapshot:

- required top-level object exists;
- trip ID equals requested trip;
- version is a positive integer;
- catalog version matches nested catalog;
- truth label, simulated and bookable literals are correct;
- planner response version equals current UI snapshot before display.

A mismatch produces `CONTRACT_MISMATCH` as a local UI error and preserves the last good snapshot. Full duplicate runtime schema libraries are optional; they cannot become a source of different domain rules.

## 42. Security contract rules

- Reject non-JSON mutation bodies before parsing.
- Enforce bytes before model validation.
- Forbid arbitrary URL fields in all P0 requests.
- Do not echo rejected free text in errors.
- Hide existence of a plan under another trip by returning `PLAN_NOT_FOUND`.
- Never serialize stack traces or database identifiers.
- Mark all P0 plans `simulated=true`, `bookable=false` through literals.
- Preserve `external_booking_executed=false` through a literal.
- Do not expose a server command that mutates Booking state.
- Provider keys are closed enums and server-configured.

## 43. Contract acceptance tests

| API ID | Criterion | Evidence |
|---|---|---|
| API-01 | Every request model rejects unknown fields | generated negative-schema suite |
| API-02 | Naive timestamps, bool/fractional/string money fail | scalar boundary tests |
| API-03 | Activity/policy/event/evidence discriminators forbid wrong subtype fields | union tests |
| API-04 | Duplicate IDs, unresolved refs and cyclic dependencies return normalized 422 | create tests |
| API-05 | Catalog scheduled data cannot be event-mutated | repository/API test |
| API-06 | D1 produces effective-service v2 state and immutable catalog hash | golden event test |
| API-07 | Identical D1 retry returns 200 duplicate and no new version | idempotency test |
| API-08 | Changed D1 payload or stale sequence returns 409 | conflict tests |
| API-09 | Constraint/current-state replacement stales previews and increments once | mutation test |
| API-10 | Planner request cannot submit prices/capacity/totals/plans | unknown-field tests |
| API-11 | Planner complete/no-plan/needs-input/partial are distinct 200 contracts | fixture cases |
| API-12 | F2/F3/F4/wait totals/status/cutoffs match Document 04 | golden response test |
| API-13 | Planner counts reconcile with returned arrays | property/response validation |
| API-14 | Plan lookup enforces trip ownership | 404 isolation test |
| API-15 | Adoption accepts only plan ID/version/true acknowledgement | request tests |
| API-16 | Adoption at exactly valid-until returns `PLAN_EXPIRED` | FX-10 boundary test |
| API-17 | Adoption response keeps bookings unchanged and external false | contract/golden test |
| API-18 | Reset returns baseline content at current+1 | reset test |
| API-19 | Oversized and wrong-media requests return 413/415 normalized problems | middleware tests |
| API-20 | Framework validation never leaks native error body | captured response tests |
| API-21 | Every snapshot is internally version/catalog coherent | response property test |
| API-22 | OpenAPI generation and TypeScript generation are diff-clean | contract CI step |
| API-23 | Every documented OpenAPI example validates | schema example test |
| API-24 | Runtime frontend guard rejects mixed-version planner result | frontend unit test |
| API-25 | P0 request/response schemas contain no PNR/Aadhaar/passport/payment/email field | schema audit |
| API-26 | Itinerary edit cannot alter completed/current prefix, original itinerary, catalog, effective services or Bookings. | guarded-edit integration test |
| API-27 | Hard-activity removal fails without literal acknowledgement and succeeds with it when otherwise valid. | guarded-edit integration test |
| API-28 | Material edit increments once and stales previews; identical edit is a no-op. | version/lifecycle integration test |
| API-29 | Edited required-commitment order and dependency DAG remain mutually compatible. | DAG/order integration test |

## 44. Traceability

| Contract area | Domain/algorithm | PRD/architecture |
|---|---|---|
| Strict input and current state | DM-01–DM-09 | FR-001–FR-004, NFR-09, ARC-13 |
| Immutable catalog/effective overlay | DM-04, DM-10 | FR-008–FR-011, ARCH-D04 |
| Event union/idempotency | ALG-01–ALG-02 | FR-008–FR-010, ARC-06–ARC-07 |
| Evaluated activities/impacts | DM-11, ALG-03–ALG-07 | FR-011–FR-013, NFR-11 |
| Planner result and scope | DM-12–DM-13, ALG-08–ALG-13 | FR-014–FR-020, ARC-05/08/16 |
| Money and policies | DM-14–DM-15, ALG-09–ALG-10 | FR-021–FR-024 |
| Adoption/lifecycle | DM-17, ALG-14–ALG-16 | FR-025–FR-030, ARC-06–ARC-09 |
| Generated frontend types | DM-O04, ARCH-O01 | FR-034, NFR-06/NFR-12 |

## 45. Decisions fixed by this specification

| Decision ID | Resolution |
|---|---|
| API-D01 | Version external application API at `/api/v1` |
| API-D02 | Use strict, frozen, extra-forbid Pydantic contract models |
| API-D03 | Use request discriminators for create source, activities, policies, events and evidence |
| API-D04 | Separate immutable ServiceDefinition from versioned EffectiveServiceState |
| API-D05 | Remove derivable planned times/latest arrival from input definitions |
| API-D06 | Use full replacement for constraints and current state |
| API-D07 | Use explicit expected version in mutation bodies |
| API-D08 | Return duplicate events as successful 200 dispositions |
| API-D09 | Represent no-plan/unknown/partial as successful domain results |
| API-D10 | Use typed EvidenceValue instead of arbitrary observed/required JSON |
| API-D11 | Return full coherent snapshots after mutations |
| API-D12 | Generate TypeScript schema types from committed OpenAPI |
| API-D13 | Omit browser deletion from fictional P0; reset remains available |
| API-D14 | Allow planner computation outside transaction but version-check before save |
| API-D15 | Keep all provider destinations behind closed provider keys |

## 46. Open items for later documents

| Open ID | Owner | Item |
|---|---|---|
| API-O01 | UX Specification | Exact mapping from every domain/API code to English display copy and actions |
| API-O02 | Test Strategy | Full golden JSON files, property generators and concurrency harness |
| API-O03 | Implementation | Exact generated OpenAPI document after models are coded |
| API-O04 | Implementation Gate A0 | Locked `openapi-typescript` and all runtime versions |
| API-O05 | Deployment Runbook | Whether packaged demo exposes local interactive OpenAPI docs |

These items cannot change field meaning, subtype rules, concurrency or truth literals without revising this document.

## 47. Approval

This contract is ready to lock when:

- A validates every domain invariant and the catalog/effective-state separation;
- B confirms all planner, money, frontier and validity outputs are representable without untyped fields;
- C confirms generated TypeScript supports every required screen and error state;
- D confirms endpoint/transaction/status mappings are implementable in the modular monolith;
- the executable fixture migration reproduces Document 04 results; and
- a generated OpenAPI smoke document contains no ambiguous unions or `additionalProperties: true` outside the declared reason-count map.

| Role | Name | Approval | Date |
|---|---|---|---|
| A — Domain/impact |  | Pending |  |
| B — Planner/finance |  | Pending |  |
| C — Product/UI |  | Pending |  |
| D — API/integration |  | Pending |  |

After approval, create **Document 08 — UX, Interaction and Demo Specification**. It must consume these exact states and fields without inventing a separate client-side calculation contract.
