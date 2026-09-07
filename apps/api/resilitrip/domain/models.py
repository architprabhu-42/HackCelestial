"""Strict Gate A1 domain contracts derived from Documents 03, 04, and 07."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator, model_validator
from typing_extensions import TypeAliasType


EntityId = Annotated[str, StringConstraints(pattern=r"^[A-Za-z0-9][A-Za-z0-9:._-]{0,127}$")]
DisplayLabel = Annotated[str, StringConstraints(min_length=1, max_length=120, strip_whitespace=True)]
MoneyPaise = Annotated[int, Field(strict=True, ge=0, le=100_000_000)]
SignedMoneyPaise = Annotated[int, Field(strict=True, ge=-100_000_000, le=100_000_000)]
NullableMoneyPaise = MoneyPaise | None
DurationSec = Annotated[int, Field(strict=True, ge=0, le=86_400)]
PositiveDurationSec = Annotated[int, Field(strict=True, ge=1, le=86_400)]
SlackSec = Annotated[int, Field(strict=True, ge=-172_800, le=172_800)]
TRUTH_LABEL = "SYNTHETIC SCENARIO " + chr(0x2014) + " NOT BOOKABLE"


class ContractModel(BaseModel):
    # FastAPI supplies decoded JSON objects, so enum/datetime wire values require
    # normal JSON coercion. Numeric contract aliases remain individually strict.
    model_config = ConfigDict(extra="forbid", strict=False, validate_assignment=True, frozen=True)

    @field_validator("*", mode="after", check_fields=False)
    @classmethod
    def aware_datetimes(cls, value: object) -> object:
        if isinstance(value, datetime) and (value.tzinfo is None or value.utcoffset() is None):
            raise ValueError("timestamp must include an explicit timezone offset")
        return value


class TripMode(StrEnum):
    DEMO = "demo"


class LocationKind(StrEnum):
    RAIL_STATION = "rail_station"
    AIRPORT_TERMINAL = "airport_terminal"
    HOTEL = "hotel"
    VENUE = "venue"
    GENERIC_POINT = "generic_point"


class FixedServiceMode(StrEnum):
    RAIL = "rail"
    AIR = "air"
    BUS = "bus"


class TransportMode(StrEnum):
    RAIL = "rail"
    AIR = "air"
    BUS = "bus"
    ROAD_TRANSFER = "road_transfer"


class TravelerPhase(StrEnum):
    NOT_STARTED = "not_started"
    AT_LOCATION = "at_location"
    ONBOARD = "onboard"
    COMPLETED = "completed"


class ServiceStatus(StrEnum):
    SCHEDULED = "scheduled"
    DELAYED = "delayed"
    CANCELLED = "cancelled"


class AccessibilityState(StrEnum):
    SUITABLE = "suitable"
    UNSUITABLE = "unsuitable"
    UNKNOWN = "unknown"


class BookingState(StrEnum):
    FICTIONAL = "fictional"
    USER_REPORTED = "user_reported"
    PROVIDER_CONFIRMED = "provider_confirmed"
    CANCELLED = "cancelled"


class RankingPreset(StrEnum):
    CHEAPEST = "cheapest"
    FASTEST = "fastest"
    FEWEST_CHANGES = "fewest_changes"


class RankingReasonCode(StrEnum):
    LOWEST_CASH_ON_FRONTIER = "LOWEST_CASH_ON_FRONTIER"
    EARLIEST_ARRIVAL_ON_FRONTIER = "EARLIEST_ARRIVAL_ON_FRONTIER"
    FEWEST_CHANGES_ON_FRONTIER = "FEWEST_CHANGES_ON_FRONTIER"
    TIE_BROKEN_BY_CASH = "TIE_BROKEN_BY_CASH"
    TIE_BROKEN_BY_ARRIVAL = "TIE_BROKEN_BY_ARRIVAL"
    TIE_BROKEN_BY_CHANGES = "TIE_BROKEN_BY_CHANGES"
    TIE_BROKEN_BY_PLAN_ID = "TIE_BROKEN_BY_PLAN_ID"


class PlanLifecycleStatus(StrEnum):
    PREVIEW = "preview"
    ADOPTED = "adopted"
    STALE = "stale"


class PlannerResultStatus(StrEnum):
    COMPLETE = "complete"
    NO_FEASIBLE_CATALOG_PLAN = "no_feasible_catalog_plan"
    NEEDS_INPUT = "needs_input"
    PARTIAL_SEARCH = "partial_search"
    ERROR = "error"


class ServicePriceState(StrEnum):
    PAID = "paid"
    DUE_IF_SELECTED = "due_if_selected"


class ActivityKind(StrEnum):
    FIXED_TRANSPORT = "fixed_transport"
    FLEXIBLE_TRANSFER = "flexible_transfer"
    PROCESSING = "processing"
    HOTEL_CHECKIN = "hotel_checkin"
    COMMITMENT = "commitment"


class FeasibilityStatus(StrEnum):
    FEASIBLE = "feasible"
    AT_RISK = "at_risk"
    INFEASIBLE = "infeasible"
    BLOCKED = "blocked"
    UNKNOWN = "unknown"


class DomainReasonCode(StrEnum):
    HARD_DEADLINE_MISSED = "HARD_DEADLINE_MISSED"
    LOW_POSITIVE_SLACK = "LOW_POSITIVE_SLACK"
    SERVICE_CANCELLED = "SERVICE_CANCELLED"
    SERVICE_CUTOFF_MISSED = "SERVICE_CUTOFF_MISSED"
    LOCATION_UNREACHABLE = "LOCATION_UNREACHABLE"
    CAPACITY_INSUFFICIENT = "CAPACITY_INSUFFICIENT"
    CAPACITY_UNKNOWN = "CAPACITY_UNKNOWN"
    ACTIVITY_WINDOW_MISSED = "ACTIVITY_WINDOW_MISSED"
    ACCESSIBILITY_UNSUITABLE = "ACCESSIBILITY_UNSUITABLE"
    ACCESSIBILITY_UNKNOWN = "ACCESSIBILITY_UNKNOWN"
    CASH_LIMIT_EXCEEDED = "CASH_LIMIT_EXCEEDED"
    EXTRA_COST_LIMIT_EXCEEDED = "EXTRA_COST_LIMIT_EXCEEDED"
    MODE_NOT_ALLOWED = "MODE_NOT_ALLOWED"
    SEARCH_HORIZON_EXCEEDED = "SEARCH_HORIZON_EXCEEDED"
    MAX_FIXED_LEGS_EXCEEDED = "MAX_FIXED_LEGS_EXCEEDED"
    MAX_TRANSFER_LEGS_EXCEEDED = "MAX_TRANSFER_LEGS_EXCEEDED"
    REQUIRED_FACT_MISSING = "REQUIRED_FACT_MISSING"
    UNSUPPORTED_CURRENT_STATE = "UNSUPPORTED_CURRENT_STATE"
    STALE_PLAN = "STALE_PLAN"
    SEARCH_INCOMPLETE = "SEARCH_INCOMPLETE"
    INVALID_DEPENDENCY_GRAPH = "INVALID_DEPENDENCY_GRAPH"
    DUPLICATE_EVENT = "DUPLICATE_EVENT"
    EVENT_ID_CONFLICT = "EVENT_ID_CONFLICT"
    EVENT_SEQUENCE_STALE = "EVENT_SEQUENCE_STALE"
    VERSION_CONFLICT = "VERSION_CONFLICT"
    POLICY_CONFIRMATION_REQUIRED = "POLICY_CONFIRMATION_REQUIRED"
    HARD_CONSTRAINTS_PASS = "HARD_CONSTRAINTS_PASS"


class ProvenanceKind(StrEnum):
    SYNTHETIC = "synthetic"
    USER_REPORTED = "user_reported"
    OFFICIAL_REPLAY = "official_replay"
    AUTHORIZED_LIVE = "authorized_live"
    ESTIMATE = "estimate"


class VerificationState(StrEnum):
    UNVERIFIED = "unverified"
    FIXTURE = "fixture"
    PROVIDER_CONFIRMED = "provider_confirmed"


class MoneyCategory(StrEnum):
    RETAINED_CHARGE = "retained_charge"
    NEW_PURCHASE = "new_purchase"
    MANDATORY_FEE = "mandatory_fee"
    POTENTIAL_REFUND = "potential_refund"
    RECEIVED_REFUND = "received_refund"
    SUNK_COST = "sunk_cost"


class PaymentState(StrEnum):
    PAID = "paid"
    DUE = "due"
    POTENTIAL = "potential"


class ProvenanceRecord(ContractModel):
    id: EntityId
    kind: ProvenanceKind
    verification: VerificationState
    observed_at: datetime
    retrieved_at: datetime
    valid_until: datetime | None
    source_ref: Annotated[str, StringConstraints(min_length=1, max_length=200)]

    @model_validator(mode="after")
    def retrieved_after_observed(self) -> "ProvenanceRecord":
        if self.retrieved_at < self.observed_at:
            raise ValueError("retrieved_at must not precede observed_at")
        return self


class Location(ContractModel):
    id: EntityId
    kind: LocationKind
    name: DisplayLabel
    code: str | None
    terminal: str | None
    latitude: Annotated[float, Field(ge=-90, le=90)]
    longitude: Annotated[float, Field(ge=-180, le=180)]
    provenance_id: EntityId
    field_provenance: tuple[object, ...] = ()

    @model_validator(mode="after")
    def location_kind_requirements(self) -> "Location":
        if self.kind is LocationKind.AIRPORT_TERMINAL and (not self.code or not self.terminal):
            raise ValueError("airport terminal requires code and terminal")
        if self.kind is LocationKind.RAIL_STATION and not self.code:
            raise ValueError("rail station requires code")
        return self


class PolicyRecord(ContractModel):
    id: EntityId
    policy_kind: Literal[
        "flexible_transfer_fictional", "hotel_retained_fictional", "new_fixed_service_fictional", "provider_guidance"
    ]
    source_class: Literal["synthetic", "official_guidance", "user_reported"]
    scope: Annotated[str, StringConstraints(min_length=1, max_length=160)]
    verification: VerificationState
    conflict: bool
    calculation_allowed: bool
    provenance_id: EntityId
    selected_price_due: bool | None = None
    abandon_before_pickup_fee_paise: MoneyPaise | None = None
    paid_paise: MoneyPaise | None = None
    additional_checkin_fee_paise: MoneyPaise | None = None
    listed_fare_due_if_selected: bool | None = None
    additional_fee_paise: MoneyPaise | None = None
    result: Literal["needs_provider_confirmation"] | None = None
    required_inputs: tuple[str, ...] = ()
    exclusions: tuple[str, ...] = ()

    @model_validator(mode="after")
    def policy_shape(self) -> "PolicyRecord":
        fictional = self.policy_kind != "provider_guidance"
        if fictional and (self.source_class != "synthetic" or self.verification is not VerificationState.FIXTURE or self.conflict or not self.calculation_allowed):
            raise ValueError("fictional policy metadata is invalid")
        if self.policy_kind == "provider_guidance" and (self.calculation_allowed or self.result != "needs_provider_confirmation"):
            raise ValueError("provider guidance cannot calculate")
        return self


class ServiceDefinition(ContractModel):
    id: EntityId
    display_code: Annotated[str, StringConstraints(min_length=1, max_length=24)]
    mode: FixedServiceMode
    service_date: str
    origin_id: EntityId
    destination_id: EntityId
    scheduled_departure: datetime
    scheduled_arrival: datetime
    origin_allowance_sec: DurationSec
    exit_allowance_sec: DurationSec
    capacity: Annotated[int, Field(strict=True, ge=0)] | None
    price_paise: NullableMoneyPaise
    price_state: ServicePriceState
    policy_id: EntityId
    provenance_id: EntityId
    field_provenance: tuple[object, ...] = ()

    @model_validator(mode="after")
    def service_chronology(self) -> "ServiceDefinition":
        if self.origin_id == self.destination_id:
            raise ValueError("service origin and destination must differ")
        if self.scheduled_arrival <= self.scheduled_departure:
            raise ValueError("service arrival must be after departure")
        return self


class TransferTemplate(ContractModel):
    id: EntityId
    display_code: Annotated[str, StringConstraints(min_length=1, max_length=32)]
    origin_id: EntityId
    destination_id: EntityId
    window_start: datetime
    latest_start: datetime
    duration_sec: PositiveDurationSec
    capacity: Annotated[int, Field(strict=True, ge=0)] | None
    price_paise: NullableMoneyPaise
    accessibility: AccessibilityState
    policy_id: EntityId
    provenance_id: EntityId
    field_provenance: tuple[object, ...] = ()

    @model_validator(mode="after")
    def transfer_window(self) -> "TransferTemplate":
        if self.origin_id == self.destination_id:
            raise ValueError("transfer origin and destination must differ")
        if self.latest_start < self.window_start:
            raise ValueError("transfer latest_start must not precede window_start")
        return self


class ServiceCatalog(ContractModel):
    schema_version: Literal["resilitrip-api-1.0"]
    catalog_version: EntityId
    scenario_id: EntityId | None
    currency: Literal["INR"]
    display_timezone: Literal["Asia/Kolkata"]
    locations: tuple[Location, ...]
    services: tuple[ServiceDefinition, ...]
    transfer_templates: tuple[TransferTemplate, ...]
    policies: tuple[PolicyRecord, ...]
    provenance: tuple[ProvenanceRecord, ...]


class TravelerProfile(ContractModel):
    party_size: Literal[1]
    display_name: DisplayLabel | None
    accessibility_required: bool


class CurrentState(ContractModel):
    as_of: datetime
    location_id: EntityId | None
    phase: TravelerPhase
    active_service_id: EntityId | None
    completed_activity_ids: tuple[EntityId, ...]
    next_recovery_point_id: EntityId | None
    provenance_id: EntityId

    @model_validator(mode="after")
    def current_state_shape(self) -> "CurrentState":
        if self.phase in (TravelerPhase.NOT_STARTED, TravelerPhase.AT_LOCATION) and (not self.location_id or self.active_service_id or self.next_recovery_point_id):
            raise ValueError("at-location states require a location and no active service")
        if self.phase is TravelerPhase.ONBOARD and not self.active_service_id:
            raise ValueError("onboard state requires active_service_id")
        if self.phase is not TravelerPhase.ONBOARD and self.next_recovery_point_id:
            raise ValueError("next recovery point is only valid onboard")
        if self.phase is TravelerPhase.COMPLETED and self.active_service_id:
            raise ValueError("completed state cannot have active service")
        return self


class Constraints(ContractModel):
    party_size: Literal[1]
    max_cash_required_paise: MoneyPaise
    max_incremental_cost_paise: MoneyPaise
    allowed_modes: tuple[TransportMode, ...]
    required_commitment_ids: tuple[EntityId, ...]
    accessibility_required: bool
    ranking_preset: RankingPreset
    max_new_fixed_legs: Annotated[int, Field(strict=True, ge=0, le=2)]
    max_transfer_legs: Annotated[int, Field(strict=True, ge=0, le=8)]
    horizon_end: datetime
    risk_threshold_sec: DurationSec


class ActivityDefinition(ContractModel):
    id: EntityId
    kind: ActivityKind
    hard: bool
    booking_id: EntityId | None
    provenance_id: EntityId | None
    service_id: EntityId | None = None
    transfer_template_id: EntityId | None = None
    location_id: EntityId | None = None
    duration_sec: PositiveDurationSec | None = None
    earliest_start: datetime | None = None
    latest_start: datetime | None = None
    start_at: datetime | None = None
    readiness_allowance_sec: DurationSec | None = None
    derived_from_service_id: EntityId | None = None

    @model_validator(mode="after")
    def activity_shape(self) -> "ActivityDefinition":
        if self.kind is ActivityKind.FIXED_TRANSPORT and self.service_id is None:
            raise ValueError("fixed transport requires service_id")
        if self.kind is ActivityKind.FLEXIBLE_TRANSFER and self.transfer_template_id is None:
            raise ValueError("flexible transfer requires transfer_template_id")
        if self.kind is ActivityKind.PROCESSING and (self.location_id is None or self.duration_sec is None):
            raise ValueError("processing requires location and duration")
        if self.kind is ActivityKind.HOTEL_CHECKIN:
            if None in (self.location_id, self.earliest_start, self.latest_start, self.duration_sec):
                raise ValueError("hotel check-in requires location, window, and duration")
            if self.latest_start < self.earliest_start:  # type: ignore[operator]
                raise ValueError("hotel window is invalid")
        if self.kind is ActivityKind.COMMITMENT and None in (self.location_id, self.start_at, self.readiness_allowance_sec):
            raise ValueError("commitment requires location, start_at, and readiness allowance")
        return self


class Dependency(ContractModel):
    id: EntityId
    from_id: EntityId
    to_id: EntityId
    buffer_sec: DurationSec
    reason: Annotated[str, StringConstraints(min_length=1, max_length=80)]


class ItineraryDefinition(ContractModel):
    activities: tuple[ActivityDefinition, ...]
    dependencies: tuple[Dependency, ...]


class Booking(ContractModel):
    id: EntityId
    state: BookingState
    service_or_activity_ids: tuple[EntityId, ...]
    paid_paise: MoneyPaise
    remaining_paise: MoneyPaise
    policy_id: EntityId
    provenance_id: EntityId


class MoneyItem(ContractModel):
    id: EntityId
    booking_id: EntityId | None
    service_id: EntityId | None
    transfer_template_id: EntityId | None
    category: MoneyCategory
    payment_state: PaymentState
    amount_paise: NullableMoneyPaise
    provenance_id: EntityId

    @model_validator(mode="after")
    def money_invariant(self) -> "MoneyItem":
        valid = {
            MoneyCategory.SUNK_COST: PaymentState.PAID,
            MoneyCategory.RECEIVED_REFUND: PaymentState.PAID,
            MoneyCategory.POTENTIAL_REFUND: PaymentState.POTENTIAL,
            MoneyCategory.RETAINED_CHARGE: PaymentState.DUE,
            MoneyCategory.NEW_PURCHASE: PaymentState.DUE,
            MoneyCategory.MANDATORY_FEE: PaymentState.DUE,
        }
        if valid[self.category] is not self.payment_state:
            raise ValueError("invalid money category/payment state")
        if self.amount_paise is None and self.category is not MoneyCategory.POTENTIAL_REFUND:
            raise ValueError("only potential refunds may have unknown money")
        return self


class EffectiveServiceState(ContractModel):
    service_id: EntityId
    effective_departure: datetime
    effective_arrival: datetime
    status: ServiceStatus
    last_event_id: EntityId | None
    provenance_id: EntityId

    @model_validator(mode="after")
    def effective_chronology(self) -> "EffectiveServiceState":
        if self.effective_arrival <= self.effective_departure:
            raise ValueError("effective arrival must be after departure")
        return self


class InstalledScenarioDefinition(ContractModel):
    id: EntityId
    name: DisplayLabel
    mode: Literal["demo"]
    display_timezone: Literal["Asia/Kolkata"]
    currency: Literal["INR"]
    truth_label: str
    replay_start: datetime
    decision_allowance_sec: DurationSec
    max_activities: Literal[20]
    max_catalog_services: Literal[50]
    max_displayed_frontier_plans: Literal[3]

    @field_validator("truth_label")
    @classmethod
    def exact_truth_label(cls, value: str) -> str:
        if value != TRUTH_LABEL:
            raise ValueError("truth_label must be the P0 synthetic/not-bookable literal")
        return value


class TimingReplayEvent(ContractModel):
    event_id: EntityId
    source_id: EntityId
    source_sequence: Annotated[int, Field(strict=True, ge=1)]
    expected_trip_version: Annotated[int, Field(strict=True, ge=1)]
    type: Literal["SERVICE_TIMING_UPDATED"]
    service_id: EntityId
    observed_at: datetime
    effective_at: datetime
    new_departure_at: datetime
    new_arrival_at: datetime
    provenance: ProvenanceRecord

    @model_validator(mode="after")
    def timing_event_chronology(self) -> "TimingReplayEvent":
        if self.new_arrival_at <= self.new_departure_at:
            raise ValueError("event arrival must be after departure")
        return self


class ServiceCancelledEvent(ContractModel):
    event_id: EntityId
    source_id: EntityId
    source_sequence: Annotated[int, Field(strict=True, ge=1)]
    expected_trip_version: Annotated[int, Field(strict=True, ge=1)]
    type: Literal["SERVICE_CANCELLED"]
    service_id: EntityId
    observed_at: datetime
    effective_at: datetime
    provenance: ProvenanceRecord


class ExecutableScenarioFixture(ContractModel):
    schema_version: Literal["resilitrip-api-1.0"]
    scenario: InstalledScenarioDefinition
    catalog: ServiceCatalog
    traveler: TravelerProfile
    current_state: CurrentState
    constraints: Constraints
    original_itinerary: ItineraryDefinition
    bookings: tuple[Booking, ...]
    baseline_money_items: tuple[MoneyItem, ...]
    trip_provenance: tuple[ProvenanceRecord, ...]
    constraints_provenance_id: EntityId
    replay_events: tuple[TimingReplayEvent, ...]


class EvaluatedActivity(ContractModel):
    activity_id: EntityId
    kind: ActivityKind
    service_id: EntityId | None
    transfer_template_id: EntityId | None
    origin_id: EntityId | None
    destination_id: EntityId | None
    start_at: datetime | None
    end_at: datetime | None
    ready_at: datetime | None
    cutoff_at: datetime | None
    slack_sec: SlackSec | None
    status: FeasibilityStatus
    reason_codes: tuple[DomainReasonCode, ...]
    provenance_ids: tuple[EntityId, ...]


class _EvidenceBase(ContractModel):
    unit: str | None


class UnknownEvidenceValue(_EvidenceBase):
    value_kind: Literal["unknown"]
    value: None


class TimestampEvidenceValue(_EvidenceBase):
    value_kind: Literal["timestamp"]
    value: datetime


class DurationEvidenceValue(_EvidenceBase):
    value_kind: Literal["duration_sec"]
    value: Annotated[int, Field(strict=True, ge=-172_800, le=172_800)]


class MoneyEvidenceValue(_EvidenceBase):
    value_kind: Literal["money_paise"]
    value: SignedMoneyPaise


class IntegerEvidenceValue(_EvidenceBase):
    value_kind: Literal["integer"]
    value: Annotated[int, Field(strict=True)]


class BooleanEvidenceValue(_EvidenceBase):
    value_kind: Literal["boolean"]
    value: Annotated[bool, Field(strict=True)]


class TextEvidenceValue(_EvidenceBase):
    value_kind: Literal["text"]
    value: Annotated[str, StringConstraints(max_length=200)]


class EntityIdEvidenceValue(_EvidenceBase):
    value_kind: Literal["entity_id"]
    value: EntityId


class StringListEvidenceValue(_EvidenceBase):
    value_kind: Literal["string_list"]
    value: Annotated[tuple[str, ...], Field(max_length=20)]

    @field_validator("value")
    @classmethod
    def unique_values(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        if len(value) != len(set(value)):
            raise ValueError("evidence list values must be unique")
        return value


EvidenceValue = TypeAliasType(
    "EvidenceValue",
    Annotated[
        UnknownEvidenceValue
        | TimestampEvidenceValue
        | DurationEvidenceValue
        | MoneyEvidenceValue
        | IntegerEvidenceValue
        | BooleanEvidenceValue
        | TextEvidenceValue
        | EntityIdEvidenceValue
        | StringListEvidenceValue,
        Field(discriminator="value_kind"),
    ],
)


_EVIDENCE_TYPES = {
    "unknown": UnknownEvidenceValue,
    "timestamp": TimestampEvidenceValue,
    "duration_sec": DurationEvidenceValue,
    "money_paise": MoneyEvidenceValue,
    "integer": IntegerEvidenceValue,
    "boolean": BooleanEvidenceValue,
    "text": TextEvidenceValue,
    "entity_id": EntityIdEvidenceValue,
    "string_list": StringListEvidenceValue,
}


def evidence_value(value_kind: str, value: object, unit: str | None = None) -> EvidenceValue:
    """Construct one exact evidence variant while keeping callers deterministic."""
    return _EVIDENCE_TYPES[value_kind](value_kind=value_kind, value=value, unit=unit)


class ConstraintCheck(ContractModel):
    constraint_id: EntityId
    passed: bool | None
    reason_code: DomainReasonCode
    observed: EvidenceValue
    required: EvidenceValue
    provenance_ids: tuple[EntityId, ...]


class ImpactRecord(ContractModel):
    activity_id: EntityId
    root_event_ids: tuple[EntityId, ...]
    causal_activity_path: tuple[EntityId, ...]
    before_status: FeasibilityStatus
    after_status: FeasibilityStatus
    before_ready_at: datetime | None
    after_ready_at: datetime | None
    cutoff_at: datetime | None
    before_slack_sec: SlackSec | None
    after_slack_sec: SlackSec | None
    reason_codes: tuple[DomainReasonCode, ...]
    constraint_checks: tuple[ConstraintCheck, ...]


class D1GoldenOutput(ContractModel):
    """Complete deterministic evaluator artifact for the required D1 replay."""
    trip_version: Literal[2]
    catalog_version: EntityId
    event_id: Literal["event:D1"]
    evaluated_itinerary: tuple[EvaluatedActivity, ...]
    constraint_checks: tuple[ConstraintCheck, ...]
    overall_status: FeasibilityStatus
    impacts: tuple[ImpactRecord, ...]


class PlanObjectiveValues(ContractModel):
    cash_required_paise: MoneyPaise
    final_required_arrival_at: datetime
    changed_original_booking_count: Annotated[int, Field(strict=True, ge=0, le=50)]


class PlanEvaluation(ContractModel):
    id: EntityId
    trip_id: EntityId
    trip_version: Annotated[int, Field(strict=True, ge=1)]
    catalog_version: EntityId
    run_id: EntityId | None
    lifecycle_status: PlanLifecycleStatus
    evaluation_status: FeasibilityStatus
    valid_until: datetime
    sequence_ids: tuple[EntityId, ...]
    sequence_signature: Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
    proposed_itinerary: ItineraryDefinition
    activity_sequence: tuple[EvaluatedActivity, ...]
    service_ids: tuple[EntityId, ...]
    transfer_template_ids: tuple[EntityId, ...]
    money_items: tuple[MoneyItem, ...]
    cash_required_paise: MoneyPaise
    incremental_cost_paise: SignedMoneyPaise
    potential_refund_paise: NullableMoneyPaise
    final_required_arrival_at: datetime
    event_slack_sec: SlackSec
    changed_original_booking_ids: tuple[EntityId, ...]
    constraint_checks: tuple[ConstraintCheck, ...]
    provenance_ids: tuple[EntityId, ...]
    objective_values: PlanObjectiveValues
    frontier_member: bool
    display_rank: Annotated[int, Field(strict=True, ge=1)] | None
    ranking_reason_code: RankingReasonCode | None
    simulated: Literal[True]
    bookable: Literal[False]
    reason_codes: tuple[DomainReasonCode, ...]


class SearchScope(ContractModel):
    catalog_version: EntityId
    replay_as_of: datetime
    horizon_end: datetime
    max_catalog_services: Annotated[int, Field(strict=True, ge=0, le=50)]
    max_new_fixed_legs: Annotated[int, Field(strict=True, ge=0, le=2)]
    max_transfer_legs: Annotated[int, Field(strict=True, ge=0, le=8)]
    max_activities: Literal[20]


class PlannerCounts(ContractModel):
    states_expanded: Annotated[int, Field(strict=True, ge=0)]
    complete_paths: Annotated[int, Field(strict=True, ge=0)]
    duplicate_paths: Annotated[int, Field(strict=True, ge=0)]
    feasible_total: Annotated[int, Field(strict=True, ge=0)]
    uncertain_total: Annotated[int, Field(strict=True, ge=0)]
    rejected_total: Annotated[int, Field(strict=True, ge=0)]
    frontier_total: Annotated[int, Field(strict=True, ge=0)]
    displayed_total: Annotated[int, Field(strict=True, ge=0)]
    pruned_by_reason: dict[DomainReasonCode, int]


class PlannerResult(ContractModel):
    run_id: EntityId
    trip_id: EntityId
    trip_version: Annotated[int, Field(strict=True, ge=1)]
    catalog_version: EntityId
    ranking_preset: RankingPreset
    result_status: PlannerResultStatus
    search_complete: bool
    interruption_reason: DomainReasonCode | None
    scope: SearchScope
    counts: PlannerCounts
    runtime_ms: Annotated[float, Field(strict=True, ge=0)]
    feasible_plans: tuple[PlanEvaluation, ...]
    uncertain_plans: tuple[PlanEvaluation, ...]
    rejected_plans: tuple[PlanEvaluation, ...]


class TripAggregate(ContractModel):
    schema_version: Literal["resilitrip-api-1.0"]
    id: EntityId
    version: Annotated[int, Field(strict=True, ge=1)]
    scenario_id: EntityId | None
    mode: Literal["demo"]
    display_timezone: Literal["Asia/Kolkata"]
    currency: Literal["INR"]
    truth_label: str
    traveler: TravelerProfile
    catalog_version: EntityId
    decision_allowance_sec: DurationSec
    current_state: CurrentState
    constraints: Constraints
    original_itinerary: ItineraryDefinition
    active_itinerary: ItineraryDefinition
    bookings: tuple[Booking, ...]
    baseline_money_items: tuple[MoneyItem, ...]
    baseline_remaining_spend_paise: MoneyPaise
    effective_services: tuple[EffectiveServiceState, ...]
    provenance: tuple[ProvenanceRecord, ...]
    constraints_provenance_id: EntityId
    adopted_plan_id: EntityId | None = None
    last_mutation_kind: Literal["created", "event", "constraints", "current_state", "itinerary_edit", "adoption", "reset"] = "created"

    @field_validator("truth_label")
    @classmethod
    def aggregate_truth_label(cls, value: str) -> str:
        if value != TRUTH_LABEL:
            raise ValueError("truth_label must be the P0 synthetic/not-bookable literal")
        return value


class AvailableActions(ContractModel):
    can_apply_event: bool
    can_edit_constraints: bool
    can_edit_current_state: bool
    can_edit_itinerary: bool
    can_generate_plans: bool
    can_adopt_plan: bool
    can_reset: bool


class TripViewSnapshot(ContractModel):
    trip: TripAggregate
    catalog: ServiceCatalog
    evaluated_itinerary: tuple[EvaluatedActivity, ...]
    overall_status: FeasibilityStatus
    impacts: tuple[ImpactRecord, ...] = ()
    provenance: tuple[ProvenanceRecord, ...]
    available_actions: AvailableActions
