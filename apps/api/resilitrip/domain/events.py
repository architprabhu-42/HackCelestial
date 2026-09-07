"""Pure timing-event application and deterministic impact diffing."""

from __future__ import annotations

from collections import deque

from resilitrip.domain.evaluation import evaluate_itinerary
from resilitrip.domain.models import (
    DomainReasonCode, EffectiveServiceState, ImpactRecord, ServiceCancelledEvent, ServiceStatus, TimingReplayEvent, TripAggregate,
)


def apply_timing_event(trip: TripAggregate, event: TimingReplayEvent) -> TripAggregate:
    matching = [item for item in trip.effective_services if item.service_id == event.service_id]
    if len(matching) != 1:
        raise ValueError("REFERENCE_NOT_FOUND")
    current = matching[0]
    if current.last_event_id == event.event_id:
        if current.effective_departure == event.new_departure_at and current.effective_arrival == event.new_arrival_at:
            return trip
        raise ValueError("EVENT_ID_CONFLICT")
    if event.expected_trip_version != trip.version:
        raise ValueError("VERSION_CONFLICT")
    changed = tuple(
        EffectiveServiceState(service_id=item.service_id, effective_departure=event.new_departure_at,
            effective_arrival=event.new_arrival_at, status=ServiceStatus.DELAYED, last_event_id=event.event_id,
            provenance_id=event.provenance.id) if item.service_id == event.service_id else item
        for item in trip.effective_services
    )
    provenance = trip.provenance if any(item.id == event.provenance.id for item in trip.provenance) else (*trip.provenance, event.provenance)
    return trip.model_copy(update={"version": trip.version + 1, "effective_services": changed,
        "provenance": provenance, "last_mutation_kind": "event"})


def apply_cancellation_event(trip: TripAggregate, event: ServiceCancelledEvent) -> TripAggregate:
    current = next((item for item in trip.effective_services if item.service_id == event.service_id), None)
    if current is None: raise ValueError("REFERENCE_NOT_FOUND")
    if current.last_event_id == event.event_id:
        if current.status is ServiceStatus.CANCELLED: return trip
        raise ValueError("EVENT_ID_CONFLICT")
    if event.expected_trip_version != trip.version: raise ValueError("VERSION_CONFLICT")
    changed=tuple(item.model_copy(update={"status":ServiceStatus.CANCELLED,"last_event_id":event.event_id,
        "provenance_id":event.provenance.id}) if item.service_id==event.service_id else item for item in trip.effective_services)
    provenance = trip.provenance if any(item.id == event.provenance.id for item in trip.provenance) else (*trip.provenance, event.provenance)
    return trip.model_copy(update={"version":trip.version+1,"effective_services":changed,
        "provenance":provenance,"last_mutation_kind":"event"})


def replace_service_state(trip: TripAggregate, service_id: str, *, departure_at=None, arrival_at=None,
                          status: ServiceStatus | None = None, event_id: str = "event:fixture-perturbation") -> TripAggregate:
    """Create an isolated immutable service-state branch for fixture perturbation tests."""
    if service_id not in {item.service_id for item in trip.effective_services}:
        raise ValueError("REFERENCE_NOT_FOUND")
    updated = tuple(item.model_copy(update={
        "effective_departure": departure_at or item.effective_departure,
        "effective_arrival": arrival_at or item.effective_arrival,
        "status": status or item.status,
        "last_event_id": event_id,
    }) if item.service_id == service_id else item for item in trip.effective_services)
    return trip.model_copy(update={"effective_services": updated})


def evaluate_trip(trip: TripAggregate, catalog, *, evaluation_mode: str) -> tuple:
    return evaluate_itinerary(itinerary=trip.active_itinerary, catalog=catalog, current_state=trip.current_state,
        effective_services=trip.effective_services, decision_allowance_sec=trip.decision_allowance_sec,
        risk_threshold_sec=trip.constraints.risk_threshold_sec, evaluation_mode=evaluation_mode)


def _shortest_path(trip: TripAggregate, root_service_id: str, target_activity_id: str) -> tuple[str, ...]:
    root = next(activity.id for activity in trip.active_itinerary.activities if activity.service_id == root_service_id)
    edges = [(edge.from_id, edge.to_id) for edge in trip.active_itinerary.dependencies]
    adjacency: dict[str, list[str]] = {}
    for source, target in edges:
        adjacency.setdefault(source, []).append(target)
    queue: deque[tuple[str, tuple[str, ...]]] = deque([(root, (root,))])
    seen = {root}
    while queue:
        node, path = queue.popleft()
        if node == target_activity_id:
            return path
        for successor in sorted(adjacency.get(node, ())):
            if successor not in seen:
                seen.add(successor)
                queue.append((successor, (*path, successor)))
    return (root,)


def calculate_impacts(before: TripAggregate, after: TripAggregate, catalog, event: TimingReplayEvent) -> tuple[ImpactRecord, ...]:
    before_items, _, _ = evaluate_trip(before, catalog, evaluation_mode="baseline")
    after_items, after_checks, _ = evaluate_trip(after, catalog, evaluation_mode="current")
    before_map = {item.activity_id: item for item in before_items}
    impacts: list[ImpactRecord] = []
    for item in after_items:
        prior = before_map[item.activity_id]
        changed = (prior.start_at, prior.end_at, prior.ready_at, prior.status, prior.slack_sec) != (item.start_at, item.end_at, item.ready_at, item.status, item.slack_sec)
        if not changed:
            continue
        reasons = item.reason_codes or (DomainReasonCode.HARD_CONSTRAINTS_PASS,)
        relevant = tuple(check for check in after_checks if check.constraint_id.startswith(f"constraint:{item.activity_id}:"))
        impacts.append(ImpactRecord(activity_id=item.activity_id, root_event_ids=(event.event_id,),
            causal_activity_path=_shortest_path(after, event.service_id, item.activity_id), before_status=prior.status,
            after_status=item.status, before_ready_at=prior.ready_at, after_ready_at=item.ready_at,
            cutoff_at=item.cutoff_at, before_slack_sec=prior.slack_sec, after_slack_sec=item.slack_sec,
            reason_codes=reasons, constraint_checks=relevant))
    return tuple(impacts)
