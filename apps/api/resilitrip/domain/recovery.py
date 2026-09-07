"""Bounded atomic recovery-candidate enumeration; no finance or ranking."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import hashlib

from resilitrip.domain.evaluation import evaluate_itinerary
from resilitrip.domain.models import (
    ActivityDefinition, ActivityKind, Dependency, EffectiveServiceState, FeasibilityStatus,
    ItineraryDefinition, ServiceCatalog, TripAggregate, TravelerPhase,
)


@dataclass(frozen=True)
class RecoveryFrontier:
    location_id: str
    decision_ready_at: datetime
    required_obligation_ids: tuple[str, ...]


@dataclass(frozen=True)
class CatalogIndexes:
    services_by_origin: dict[str, tuple[str, ...]]
    transfers_by_origin: dict[str, tuple[str, ...]]


@dataclass(frozen=True)
class SearchLabel:
    location_id: str
    ready_at: datetime
    next_obligation_index: int
    steps: tuple[str, ...]
    used_service_ids: frozenset[str]
    used_transfer_ids: frozenset[str]
    new_fixed_leg_count: int
    transfer_leg_count: int


@dataclass(frozen=True)
class AtomicCandidate:
    id: str
    signature: str
    sequence: tuple[str, ...]
    itinerary: ItineraryDefinition
    status: FeasibilityStatus


def derive_recovery_frontier(trip: TripAggregate) -> RecoveryFrontier:
    state = trip.current_state
    if state.phase is TravelerPhase.ONBOARD:
        if not state.next_recovery_point_id:
            raise ValueError("UNSUPPORTED_CURRENT_STATE")
        raise ValueError("ONBOARD_RECOVERY_NOT_IMPLEMENTED")
    if state.location_id is None:
        raise ValueError("UNSUPPORTED_CURRENT_STATE")
    obligations = tuple(
        activity.id for activity in trip.original_itinerary.activities
        if activity.id in trip.constraints.required_commitment_ids
    )
    # Original dependency order, not request ordering, is authoritative.
    ordered = tuple(activity.id for activity in trip.original_itinerary.activities if activity.id in obligations)
    return RecoveryFrontier(state.location_id, state.as_of + timedelta(seconds=trip.decision_allowance_sec), ordered)


def build_catalog_indexes(catalog: ServiceCatalog, effective_services: tuple[EffectiveServiceState, ...]) -> CatalogIndexes:
    effective = {item.service_id: item for item in effective_services}
    services: dict[str, list[tuple[datetime, str]]] = {}
    for service in catalog.services:
        services.setdefault(service.origin_id, []).append((effective[service.id].effective_departure, service.id))
    transfers: dict[str, list[tuple[datetime, str]]] = {}
    for transfer in catalog.transfer_templates:
        transfers.setdefault(transfer.origin_id, []).append((transfer.window_start, transfer.id))
    return CatalogIndexes(
        services_by_origin={origin: tuple(item[1] for item in sorted(values)) for origin, values in services.items()},
        transfers_by_origin={origin: tuple(item[1] for item in sorted(values)) for origin, values in transfers.items()},
    )


def _candidate_id(steps: tuple[str, ...], trip_version: int) -> str:
    fixed = next((step for step in steps if step.startswith("svc:F")), None)
    return f"plan:{fixed.split(':')[1].split(':')[0]}:v{trip_version}" if fixed else f"plan:WAIT-T1:v{trip_version}"


def _materialize(trip: TripAggregate, catalog: ServiceCatalog, steps: tuple[str, ...]) -> ItineraryDefinition:
    original = {item.id: item for item in trip.original_itinerary.activities}
    services = {item.id: item for item in catalog.services}
    transfers = {item.id: item for item in catalog.transfer_templates}
    activities: list[ActivityDefinition] = []
    for step in steps:
        if step in services:
            service = services[step]
            activities.append(ActivityDefinition(id=step, kind=ActivityKind.FIXED_TRANSPORT, hard=True,
                booking_id=None, provenance_id=service.provenance_id, service_id=step))
            if service.exit_allowance_sec:
                activities.append(ActivityDefinition(id=f"process:{service.display_code}-exit", kind=ActivityKind.PROCESSING,
                    hard=True, booking_id=None, provenance_id=service.provenance_id, location_id=service.destination_id,
                    duration_sec=service.exit_allowance_sec, derived_from_service_id=step))
        elif step in transfers:
            transfer = transfers[step]
            activities.append(ActivityDefinition(id=step, kind=ActivityKind.FLEXIBLE_TRANSFER, hard=True,
                booking_id=None, provenance_id=transfer.provenance_id, transfer_template_id=step))
        else:
            activities.append(original[step])
    dependencies = tuple(Dependency(id=f"dep:candidate:{index}", from_id=activities[index].id,
        to_id=activities[index + 1].id, buffer_sec=0, reason="candidate_sequence") for index in range(len(activities) - 1))
    return ItineraryDefinition(activities=tuple(activities), dependencies=dependencies)


def enumerate_atomic_candidates(trip: TripAggregate, catalog: ServiceCatalog) -> tuple[AtomicCandidate, ...]:
    """Deterministically enumerate the bounded fixture graph using atomic catalog records."""
    frontier = derive_recovery_frontier(trip)
    indexes = build_catalog_indexes(catalog, trip.effective_services)
    services = {item.id: item for item in catalog.services}
    transfers = {item.id: item for item in catalog.transfer_templates}
    obligations = {item.id: item for item in trip.original_itinerary.activities if item.id in frontier.required_obligation_ids}
    original_service_ids = {item.service_id for item in trip.original_itinerary.activities if item.service_id}
    effective = {item.service_id: item for item in trip.effective_services}
    stack = [SearchLabel(frontier.location_id, frontier.decision_ready_at, 0, (), frozenset(), frozenset(), 0, 0)]
    candidates: dict[str, AtomicCandidate] = {}
    while stack:
        label = stack.pop()
        if len(label.steps) >= 20 or label.ready_at > trip.constraints.horizon_end:
            continue
        if label.next_obligation_index == len(frontier.required_obligation_ids):
            itinerary = _materialize(trip, catalog, label.steps)
            _, _, status = evaluate_itinerary(itinerary=itinerary, catalog=catalog, current_state=trip.current_state,
                effective_services=trip.effective_services, decision_allowance_sec=trip.decision_allowance_sec,
                risk_threshold_sec=trip.constraints.risk_threshold_sec, evaluation_mode="current")
            canonical = "|".join((str(trip.version), trip.catalog_version, *(activity.id for activity in itinerary.activities)))
            signature = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
            candidate = AtomicCandidate(_candidate_id(label.steps, trip.version), signature, tuple(
                activity.id for activity in itinerary.activities), itinerary, status)
            candidates.setdefault(signature, candidate)
            continue
        obligation_id = frontier.required_obligation_ids[label.next_obligation_index]
        obligation = obligations[obligation_id]
        successors: list[SearchLabel] = []
        if label.location_id == obligation.location_id:
            if obligation.kind is ActivityKind.HOTEL_CHECKIN:
                start = max(label.ready_at, obligation.earliest_start)  # type: ignore[arg-type]
                if start <= obligation.latest_start:  # type: ignore[operator]
                    successors.append(SearchLabel(label.location_id, start + timedelta(seconds=obligation.duration_sec or 0),
                        label.next_obligation_index + 1, (*label.steps, obligation.id), label.used_service_ids,
                        label.used_transfer_ids, label.new_fixed_leg_count, label.transfer_leg_count))
            else:
                successors.append(SearchLabel(label.location_id, obligation.start_at, label.next_obligation_index + 1,
                    (*label.steps, obligation.id), label.used_service_ids, label.used_transfer_ids,
                    label.new_fixed_leg_count, label.transfer_leg_count))
        else:
            for service_id in indexes.services_by_origin.get(label.location_id, ()):
                is_new = service_id not in original_service_ids
                if service_id in label.used_service_ids or (is_new and label.new_fixed_leg_count >= trip.constraints.max_new_fixed_legs):
                    continue
                service, state = services[service_id], effective[service_id]
                cutoff = state.effective_departure - timedelta(seconds=service.origin_allowance_sec)
                if label.ready_at <= cutoff:
                    successors.append(SearchLabel(service.destination_id, state.effective_arrival + timedelta(seconds=service.exit_allowance_sec),
                        label.next_obligation_index, (*label.steps, service_id), label.used_service_ids | {service_id},
                        label.used_transfer_ids, label.new_fixed_leg_count + int(is_new), label.transfer_leg_count))
            for transfer_id in indexes.transfers_by_origin.get(label.location_id, ()):
                if transfer_id in label.used_transfer_ids or label.transfer_leg_count >= trip.constraints.max_transfer_legs:
                    continue
                transfer = transfers[transfer_id]
                start = max(label.ready_at, transfer.window_start)
                if start <= transfer.latest_start:
                    successors.append(SearchLabel(transfer.destination_id, start + timedelta(seconds=transfer.duration_sec),
                        label.next_obligation_index, (*label.steps, transfer_id), label.used_service_ids,
                        label.used_transfer_ids | {transfer_id}, label.new_fixed_leg_count, label.transfer_leg_count + 1))
        stack.extend(reversed(successors))
    return tuple(sorted(candidates.values(), key=lambda candidate: candidate.id))
