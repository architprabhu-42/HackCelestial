"""Aggregate and graph validation for Gate A1 fixtures."""

from __future__ import annotations

import networkx as nx

from resilitrip.domain.models import (
    Booking, Constraints, CurrentState, ExecutableScenarioFixture, ItineraryDefinition,
    MoneyItem, ProvenanceRecord, ServiceCatalog, TravelerProfile,
)


class DomainValidationError(ValueError):
    """Normalized domain validation failure with a stable code and path."""

    def __init__(self, code: str, path: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.path = path


def _unique(values: list[str], path: str) -> None:
    if len(values) != len(set(values)):
        raise DomainValidationError("DUPLICATE_ID", path, "IDs must be unique")


def validate_dependency_dag(itinerary: ItineraryDefinition) -> None:
    """Validate a standalone replacement itinerary before it can become active."""
    ids = {item.id for item in itinerary.activities}
    _unique([item.id for item in itinerary.activities], "/activities")
    _unique([item.id for item in itinerary.dependencies], "/dependencies")
    if any(edge.from_id not in ids or edge.to_id not in ids for edge in itinerary.dependencies):
        raise DomainValidationError("REFERENCE_NOT_FOUND", "/dependencies", "dependency endpoint does not resolve")
    graph = nx.DiGraph()
    graph.add_nodes_from(ids)
    graph.add_edges_from((item.from_id, item.to_id) for item in itinerary.dependencies)
    if not nx.is_directed_acyclic_graph(graph):
        raise DomainValidationError("INVALID_DEPENDENCY_GRAPH", "/dependencies", "dependencies must form a DAG")


def validate_manual_trip(
    *, catalog: ServiceCatalog, traveler: TravelerProfile, current_state: CurrentState,
    constraints: Constraints, itinerary: ItineraryDefinition, bookings: tuple[Booking, ...],
    money_items: tuple[MoneyItem, ...], provenance: tuple[ProvenanceRecord, ...],
    constraints_provenance_id: str, booking_activity_ids: tuple[str, ...] | None = None,
) -> None:
    """Validate manual-create references using the same aggregate invariants as fixtures."""
    collections = (
        (catalog.provenance, "/catalog/provenance"), (catalog.locations, "/catalog/locations"),
        (catalog.services, "/catalog/services"), (catalog.transfer_templates, "/catalog/transfer_templates"),
        (catalog.policies, "/catalog/policies"), (bookings, "/bookings"),
        (money_items, "/baseline_money_items"), (provenance, "/trip_provenance"),
    )
    for items, path in collections:
        _unique([item.id for item in items], path)
    validate_dependency_dag(itinerary)
    location_ids = {item.id for item in catalog.locations}
    service_ids = {item.id for item in catalog.services}
    transfer_ids = {item.id for item in catalog.transfer_templates}
    policy_ids = {item.id for item in catalog.policies}
    booking_ids = {item.id for item in bookings}
    provenance_ids = {item.id for item in (*catalog.provenance, *provenance)}
    activity_ids = {item.id for item in itinerary.activities}
    if current_state.location_id is not None and current_state.location_id not in location_ids:
        raise DomainValidationError("REFERENCE_NOT_FOUND", "/current_state/location_id", "current location does not resolve")
    if current_state.active_service_id is not None and current_state.active_service_id not in service_ids:
        raise DomainValidationError("REFERENCE_NOT_FOUND", "/current_state/active_service_id", "active service does not resolve")
    if current_state.next_recovery_point_id is not None and current_state.next_recovery_point_id not in location_ids:
        raise DomainValidationError("REFERENCE_NOT_FOUND", "/current_state/next_recovery_point_id", "recovery point does not resolve")
    if any(item not in activity_ids for item in current_state.completed_activity_ids):
        raise DomainValidationError("REFERENCE_NOT_FOUND", "/current_state/completed_activity_ids", "completed activity does not resolve")
    if current_state.provenance_id not in provenance_ids:
        raise DomainValidationError("REFERENCE_NOT_FOUND", "/current_state/provenance_id", "current-state provenance does not resolve")
    if constraints_provenance_id not in {item.id for item in provenance}:
        raise DomainValidationError("REFERENCE_NOT_FOUND", "/constraints_provenance_id", "constraints provenance does not resolve")
    if traveler.accessibility_required != constraints.accessibility_required:
        raise DomainValidationError("VALIDATION_ERROR", "/constraints/accessibility_required", "traveler and constraints disagree")
    if constraints.horizon_end <= current_state.as_of:
        raise DomainValidationError("VALIDATION_ERROR", "/constraints/horizon_end", "search horizon must follow current time")
    _unique([item.value for item in constraints.allowed_modes], "/constraints/allowed_modes")
    _unique(list(constraints.required_commitment_ids), "/constraints/required_commitment_ids")
    _unique(list(current_state.completed_activity_ids), "/current_state/completed_activity_ids")
    if any(item not in activity_ids for item in constraints.required_commitment_ids):
        raise DomainValidationError("REFERENCE_NOT_FOUND", "/constraints/required_commitment_ids", "required activity does not resolve")
    for service in catalog.services:
        if service.origin_id not in location_ids or service.destination_id not in location_ids or service.policy_id not in policy_ids:
            raise DomainValidationError("REFERENCE_NOT_FOUND", "/catalog/services", "service reference does not resolve")
    for transfer in catalog.transfer_templates:
        if transfer.origin_id not in location_ids or transfer.destination_id not in location_ids or transfer.policy_id not in policy_ids:
            raise DomainValidationError("REFERENCE_NOT_FOUND", "/catalog/transfer_templates", "transfer reference does not resolve")
    for activity in itinerary.activities:
        if activity.provenance_id is not None and activity.provenance_id not in provenance_ids:
            raise DomainValidationError("REFERENCE_NOT_FOUND", "/original_itinerary/activities", "activity provenance does not resolve")
        if activity.booking_id is not None and activity.booking_id not in booking_ids:
            raise DomainValidationError("REFERENCE_NOT_FOUND", "/original_itinerary/activities", "booking does not resolve")
        if activity.service_id is not None and activity.service_id not in service_ids:
            raise DomainValidationError("REFERENCE_NOT_FOUND", "/original_itinerary/activities", "service does not resolve")
        if activity.transfer_template_id is not None and activity.transfer_template_id not in transfer_ids:
            raise DomainValidationError("REFERENCE_NOT_FOUND", "/original_itinerary/activities", "transfer does not resolve")
        if activity.location_id is not None and activity.location_id not in location_ids:
            raise DomainValidationError("REFERENCE_NOT_FOUND", "/original_itinerary/activities", "location does not resolve")
    for booking in bookings:
        if booking.policy_id not in policy_ids or booking.provenance_id not in provenance_ids:
            raise DomainValidationError("REFERENCE_NOT_FOUND", "/bookings", "booking policy/provenance does not resolve")
        valid_booking_activity_ids = set(booking_activity_ids) if booking_activity_ids is not None else activity_ids
        if any(item not in valid_booking_activity_ids and item not in service_ids for item in booking.service_or_activity_ids):
            raise DomainValidationError("REFERENCE_NOT_FOUND", "/bookings/service_or_activity_ids", "booking target does not resolve")
    for item in money_items:
        if item.provenance_id not in provenance_ids or (item.booking_id is not None and item.booking_id not in booking_ids):
            raise DomainValidationError("REFERENCE_NOT_FOUND", "/baseline_money_items", "money reference does not resolve")
        if item.service_id is not None and item.service_id not in service_ids:
            raise DomainValidationError("REFERENCE_NOT_FOUND", "/baseline_money_items/service_id", "money service does not resolve")
        if item.transfer_template_id is not None and item.transfer_template_id not in transfer_ids:
            raise DomainValidationError("REFERENCE_NOT_FOUND", "/baseline_money_items/transfer_template_id", "money transfer does not resolve")

    def endpoints(activity_id: str) -> tuple[str, str]:
        activity = next(item for item in itinerary.activities if item.id == activity_id)
        if activity.service_id:
            service = next(item for item in catalog.services if item.id == activity.service_id)
            return service.origin_id, service.destination_id
        if activity.transfer_template_id:
            transfer = next(item for item in catalog.transfer_templates if item.id == activity.transfer_template_id)
            return transfer.origin_id, transfer.destination_id
        assert activity.location_id is not None
        return activity.location_id, activity.location_id
    for dependency in itinerary.dependencies:
        if endpoints(dependency.from_id)[1] != endpoints(dependency.to_id)[0]:
            raise DomainValidationError("VALIDATION_ERROR", "/original_itinerary/dependencies", "dependency locations are discontinuous")


def validate_fixture(fixture: ExecutableScenarioFixture) -> None:
    """Validate cross references, collection uniqueness, and the itinerary DAG."""
    catalog = fixture.catalog
    _unique([item.id for item in catalog.provenance], "/catalog/provenance")
    _unique([item.id for item in fixture.trip_provenance], "/trip_provenance")
    _unique([item.id for item in catalog.locations], "/catalog/locations")
    _unique([item.id for item in catalog.services], "/catalog/services")
    _unique([item.id for item in catalog.transfer_templates], "/catalog/transfer_templates")
    _unique([item.id for item in catalog.policies], "/catalog/policies")
    _unique([item.id for item in fixture.original_itinerary.activities], "/original_itinerary/activities")
    _unique([item.id for item in fixture.original_itinerary.dependencies], "/original_itinerary/dependencies")
    _unique([item.id for item in fixture.bookings], "/bookings")
    _unique([item.id for item in fixture.baseline_money_items], "/baseline_money_items")

    provenance_ids = {item.id for item in (*catalog.provenance, *fixture.trip_provenance)}
    location_ids = {item.id for item in catalog.locations}
    policy_ids = {item.id for item in catalog.policies}
    service_ids = {item.id for item in catalog.services}
    transfer_ids = {item.id for item in catalog.transfer_templates}
    activity_ids = {item.id for item in fixture.original_itinerary.activities}
    booking_ids = {item.id for item in fixture.bookings}

    for item in (*catalog.locations, *catalog.services, *catalog.transfer_templates, *catalog.policies):
        if item.provenance_id not in provenance_ids:
            raise DomainValidationError("REFERENCE_NOT_FOUND", "/catalog", "provenance reference does not resolve")
    for service in catalog.services:
        if service.origin_id not in location_ids or service.destination_id not in location_ids or service.policy_id not in policy_ids:
            raise DomainValidationError("REFERENCE_NOT_FOUND", "/catalog/services", "service reference does not resolve")
    for transfer in catalog.transfer_templates:
        if transfer.origin_id not in location_ids or transfer.destination_id not in location_ids or transfer.policy_id not in policy_ids:
            raise DomainValidationError("REFERENCE_NOT_FOUND", "/catalog/transfer_templates", "transfer reference does not resolve")
    for activity in fixture.original_itinerary.activities:
        if activity.provenance_id is not None and activity.provenance_id not in provenance_ids:
            raise DomainValidationError("REFERENCE_NOT_FOUND", "/original_itinerary/activities", "activity provenance does not resolve")
        if activity.booking_id is not None and activity.booking_id not in booking_ids:
            raise DomainValidationError("REFERENCE_NOT_FOUND", "/original_itinerary/activities", "booking does not resolve")
        if activity.service_id is not None and activity.service_id not in service_ids:
            raise DomainValidationError("REFERENCE_NOT_FOUND", "/original_itinerary/activities", "service does not resolve")
        if activity.transfer_template_id is not None and activity.transfer_template_id not in transfer_ids:
            raise DomainValidationError("REFERENCE_NOT_FOUND", "/original_itinerary/activities", "transfer does not resolve")
        if activity.location_id is not None and activity.location_id not in location_ids:
            raise DomainValidationError("REFERENCE_NOT_FOUND", "/original_itinerary/activities", "location does not resolve")
    for dependency in fixture.original_itinerary.dependencies:
        if dependency.from_id not in activity_ids or dependency.to_id not in activity_ids:
            raise DomainValidationError("REFERENCE_NOT_FOUND", "/original_itinerary/dependencies", "dependency endpoint does not resolve")
    graph = nx.DiGraph()
    graph.add_nodes_from(activity_ids)
    graph.add_edges_from((item.from_id, item.to_id) for item in fixture.original_itinerary.dependencies)
    if not nx.is_directed_acyclic_graph(graph):
        raise DomainValidationError("DEPENDENCY_CYCLE", "/original_itinerary/dependencies", "dependencies must form a DAG")
    def endpoints(activity_id: str) -> tuple[str, str]:
        activity = next(item for item in fixture.original_itinerary.activities if item.id == activity_id)
        if activity.service_id:
            service = next(item for item in catalog.services if item.id == activity.service_id)
            return service.origin_id, service.destination_id
        if activity.transfer_template_id:
            transfer = next(item for item in catalog.transfer_templates if item.id == activity.transfer_template_id)
            return transfer.origin_id, transfer.destination_id
        assert activity.location_id is not None
        return activity.location_id, activity.location_id
    for dependency in fixture.original_itinerary.dependencies:
        if endpoints(dependency.from_id)[1] != endpoints(dependency.to_id)[0]:
            raise DomainValidationError("LOCATION_UNREACHABLE", "/original_itinerary/dependencies", "dependency locations are discontinuous")
    if fixture.current_state.location_id not in location_ids:
        raise DomainValidationError("REFERENCE_NOT_FOUND", "/current_state/location_id", "current location does not resolve")
    if fixture.constraints_provenance_id not in {item.id for item in fixture.trip_provenance}:
        raise DomainValidationError("REFERENCE_NOT_FOUND", "/constraints_provenance_id", "constraints provenance does not resolve")
    if fixture.traveler.accessibility_required != fixture.constraints.accessibility_required:
        raise DomainValidationError("CONSTRAINT_MISMATCH", "/constraints/accessibility_required", "traveler and constraints disagree")
    if any(item not in activity_ids for item in fixture.constraints.required_commitment_ids):
        raise DomainValidationError("REFERENCE_NOT_FOUND", "/constraints/required_commitment_ids", "required activity does not resolve")
    due_total = sum(item.amount_paise or 0 for item in fixture.baseline_money_items if item.payment_state.value == "due")
    if due_total != 130_000:
        raise DomainValidationError("BASELINE_MONEY_MISMATCH", "/baseline_money_items", "baseline remaining spend must be 130000 paise")
