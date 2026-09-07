"""Exportable HTTP request/response contracts; routes may remain unavailable in A1."""

from __future__ import annotations

from enum import StrEnum
from datetime import datetime
from typing import Annotated, Literal

from pydantic import Field

from resilitrip.domain.models import (
    Booking, Constraints, ContractModel, CurrentState, DisplayLabel, EntityId,
    EvidenceValue, ExecutableScenarioFixture, ItineraryDefinition, MoneyItem, ProvenanceRecord,
    PlanEvaluation, PlannerResult, RankingPreset, ServiceCancelledEvent, ServiceCatalog, TimingReplayEvent, TravelerProfile, TripViewSnapshot,
)


class ApiErrorCode(StrEnum):
    INVALID_JSON = "INVALID_JSON"
    INVALID_REQUEST = "INVALID_REQUEST"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    UNKNOWN_FIELD = "UNKNOWN_FIELD"
    MISSING_FIELD = "MISSING_FIELD"
    INVALID_DISCRIMINATOR = "INVALID_DISCRIMINATOR"
    INVALID_TIMEZONE = "INVALID_TIMEZONE"
    INVALID_MONEY = "INVALID_MONEY"
    DUPLICATE_ID = "DUPLICATE_ID"
    REFERENCE_NOT_FOUND = "REFERENCE_NOT_FOUND"
    INVALID_DEPENDENCY_GRAPH = "INVALID_DEPENDENCY_GRAPH"
    INVALID_CURRENT_STATE = "INVALID_CURRENT_STATE"
    BASELINE_RECONCILIATION_FAILED = "BASELINE_RECONCILIATION_FAILED"
    TRIP_NOT_FOUND = "TRIP_NOT_FOUND"
    SCENARIO_NOT_FOUND = "SCENARIO_NOT_FOUND"
    PLAN_NOT_FOUND = "PLAN_NOT_FOUND"
    CATALOG_VERSION_CONFLICT = "CATALOG_VERSION_CONFLICT"
    PROVENANCE_ID_CONFLICT = "PROVENANCE_ID_CONFLICT"
    PLAN_EXPIRED = "PLAN_EXPIRED"
    PLAN_NOT_ADOPTABLE = "PLAN_NOT_ADOPTABLE"
    RESET_NOT_SUPPORTED = "RESET_NOT_SUPPORTED"
    SIMULATION_ACKNOWLEDGEMENT_REQUIRED = "SIMULATION_ACKNOWLEDGEMENT_REQUIRED"
    REQUEST_TOO_LARGE = "REQUEST_TOO_LARGE"
    UNSUPPORTED_MEDIA_TYPE = "UNSUPPORTED_MEDIA_TYPE"
    INTERNAL_DATA_INTEGRITY_ERROR = "INTERNAL_DATA_INTEGRITY_ERROR"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    EVENT_ID_CONFLICT = "EVENT_ID_CONFLICT"
    EVENT_SEQUENCE_STALE = "EVENT_SEQUENCE_STALE"
    VERSION_CONFLICT = "VERSION_CONFLICT"
    STALE_PLAN = "STALE_PLAN"
    COMPLETED_ACTIVITY_IMMUTABLE = "COMPLETED_ACTIVITY_IMMUTABLE"
    ACTIVE_ACTIVITY_IMMUTABLE = "ACTIVE_ACTIVITY_IMMUTABLE"
    HARD_CHANGE_ACKNOWLEDGEMENT_REQUIRED = "HARD_CHANGE_ACKNOWLEDGEMENT_REQUIRED"
    ITINERARY_EDIT_INVALID = "ITINERARY_EDIT_INVALID"


class ProblemFieldError(ContractModel):
    path: str
    code: str
    message: str
    rejected_value: EvidenceValue | None = None


class ProblemDetail(ContractModel):
    code: ApiErrorCode
    message: str
    request_id: str
    retryable: bool
    field_errors: tuple[ProblemFieldError, ...] = ()
    current_trip_version: int | None = None
    current_catalog_version: EntityId | None = None


class ProblemResponse(ContractModel):
    error: ProblemDetail


class LiveHealthResponse(ContractModel):
    status: Literal["ok"] = "ok"
    service: Literal["resilitrip"] = "resilitrip"
    contract_version: Literal["resilitrip-api-1.0"] = "resilitrip-api-1.0"


class ReadyHealthResponse(LiveHealthResponse):
    database: Literal["ok"] = "ok"
    schema_revision: Annotated[str, Field(min_length=1, max_length=64)]
    installed_scenario_count: Annotated[int, Field(strict=True, ge=0)]


class ScenarioSummary(ContractModel):
    id: EntityId
    name: DisplayLabel
    catalog_version: EntityId
    display_timezone: Literal["Asia/Kolkata"]
    currency: Literal["INR"]
    truth_label: str
    available: bool


class FixtureTripCreate(ContractModel):
    source_type: Literal["fixture"]
    scenario_id: EntityId
    display_name: DisplayLabel | None


class ManualTripCreate(ContractModel):
    source_type: Literal["manual"]
    display_timezone: Literal["Asia/Kolkata"]
    decision_allowance_sec: int
    traveler: TravelerProfile
    catalog: ServiceCatalog
    current_state: CurrentState
    constraints: Constraints
    original_itinerary: ItineraryDefinition
    bookings: tuple[Booking, ...]
    baseline_money_items: tuple[MoneyItem, ...]
    trip_provenance: tuple[ProvenanceRecord, ...]
    constraints_provenance_id: EntityId


TripCreateRequest = Annotated[FixtureTripCreate | ManualTripCreate, Field(discriminator="source_type")]
EventCommand = Annotated[TimingReplayEvent | ServiceCancelledEvent, Field(discriminator="type")]


class ConstraintsReplaceCommand(ContractModel):
    expected_trip_version: Annotated[int, Field(strict=True, ge=1)]
    constraints: Constraints
    provenance: ProvenanceRecord


class CurrentStateReplaceCommand(ContractModel):
    expected_trip_version: Annotated[int, Field(strict=True, ge=1)]
    current_state: CurrentState
    provenance: ProvenanceRecord


class ItineraryEditCommand(ContractModel):
    expected_trip_version: Annotated[int, Field(strict=True, ge=1)]
    active_itinerary: ItineraryDefinition
    constraints: Constraints
    acknowledge_hard_changes: Annotated[bool, Field(strict=True)]
    provenance: ProvenanceRecord


class PlannerCommand(ContractModel):
    expected_trip_version: Annotated[int, Field(strict=True, ge=1)]
    expected_catalog_version: EntityId
    ranking_preset: RankingPreset


class AdoptionCommand(ContractModel):
    expected_trip_version: Annotated[int, Field(strict=True, ge=1)]
    plan_id: EntityId
    acknowledge_simulation: Literal[True]


class ResetCommand(ContractModel):
    expected_trip_version: Annotated[int, Field(strict=True, ge=1)]
    scenario_id: EntityId


class TripCreatedResponse(ContractModel):
    trip_id: EntityId
    trip_version: Annotated[int, Field(strict=True, ge=1)]
    catalog_version: EntityId
    snapshot: TripViewSnapshot


class TripSnapshotResponse(ContractModel):
    snapshot: TripViewSnapshot


class MutationResponse(ContractModel):
    mutation_kind: Literal["created", "event", "constraints", "current_state", "itinerary_edit", "adoption", "reset"]
    changed: bool
    prior_trip_version: Annotated[int, Field(strict=True, ge=1)]
    current_trip_version: Annotated[int, Field(strict=True, ge=1)]
    staled_plan_count: Annotated[int, Field(strict=True, ge=0)]
    snapshot: TripViewSnapshot


class PlannerResponse(ContractModel):
    planner_result: PlannerResult
    snapshot_version: Annotated[int, Field(strict=True, ge=1)]
    catalog_version: EntityId


class EventResult(ContractModel):
    disposition: Literal["applied", "duplicate"]
    applied: bool
    event_id: EntityId
    prior_trip_version: Annotated[int, Field(strict=True, ge=1)]
    current_trip_version: Annotated[int, Field(strict=True, ge=1)]
    snapshot: TripViewSnapshot


class AdoptionRecord(ContractModel):
    id: EntityId
    trip_id: EntityId
    plan_id: EntityId
    prior_trip_version: Annotated[int, Field(strict=True, ge=1)]
    resulting_trip_version: Annotated[int, Field(strict=True, ge=2)]
    catalog_version: EntityId
    adopted_at: datetime
    acknowledge_simulation: Literal[True]
    external_booking_executed: Literal[False]


class ProviderAction(ContractModel):
    id: EntityId
    title: DisplayLabel
    provider_key: Literal["indian_rail_enquiry", "airline_or_ota", "hotel", "local_transfer"]
    status: Literal["not_started"]
    required_before_external_change: bool
    reason: Annotated[str, Field(min_length=1, max_length=240)]
    handoff_available: bool


class AdoptionResponse(ContractModel):
    adoption: AdoptionRecord
    provider_actions: tuple[ProviderAction, ...]
    snapshot: TripViewSnapshot


class EventResponse(ContractModel):
    event_result: EventResult
