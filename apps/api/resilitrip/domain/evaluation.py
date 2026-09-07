"""Shared deterministic selected-itinerary evaluator for impact and later planning."""

from __future__ import annotations

from datetime import datetime, timedelta

import networkx as nx

from resilitrip.domain.constraints import classify_slack
from resilitrip.domain.models import (
    ActivityKind, ConstraintCheck, CurrentState, DomainReasonCode, EffectiveServiceState,
    EvaluatedActivity, EvidenceValue, FeasibilityStatus, ItineraryDefinition, ServiceCatalog,
    evidence_value,
)


def _timestamp(value: datetime | None) -> EvidenceValue:
    return evidence_value("timestamp" if value else "unknown", value, None)


def _seconds(value: int | None) -> EvidenceValue:
    return evidence_value("duration_sec" if value is not None else "unknown", value, "seconds" if value is not None else None)


def _check(identifier: str, passed: bool | None, reason: DomainReasonCode, observed: EvidenceValue, required: EvidenceValue, provenance: tuple[str, ...] = ()) -> ConstraintCheck:
    return ConstraintCheck(constraint_id=identifier, passed=passed, reason_code=reason, observed=observed, required=required, provenance_ids=provenance)


def evaluate_itinerary(
    *,
    itinerary: ItineraryDefinition,
    catalog: ServiceCatalog,
    current_state: CurrentState,
    effective_services: tuple[EffectiveServiceState, ...],
    decision_allowance_sec: int,
    risk_threshold_sec: int,
    evaluation_mode: str,
) -> tuple[tuple[EvaluatedActivity, ...], tuple[ConstraintCheck, ...], FeasibilityStatus]:
    """Evaluate a complete DAG without mutating catalog, trip, or effective state."""
    if evaluation_mode not in {"baseline", "current"}:
        raise ValueError("evaluation_mode must be baseline or current")
    services = {item.id: item for item in catalog.services}
    effective = {item.service_id: item for item in effective_services}
    transfers = {item.id: item for item in catalog.transfer_templates}
    activities = {item.id: item for item in itinerary.activities}
    graph = nx.DiGraph()
    graph.add_nodes_from(activities)
    graph.add_edges_from((edge.from_id, edge.to_id) for edge in itinerary.dependencies)
    order = list(nx.lexicographical_topological_sort(graph, key=lambda value: value))
    ready: dict[str, datetime] = {}
    locations: dict[str, str | None] = {}
    status: dict[str, FeasibilityStatus] = {}
    results: list[EvaluatedActivity] = []
    checks: list[ConstraintCheck] = []
    initial_ready = current_state.as_of + timedelta(seconds=decision_allowance_sec)

    for activity_id in order:
        activity = activities[activity_id]
        predecessors = sorted(graph.predecessors(activity_id))
        predecessor_ready = max((ready[item] for item in predecessors), default=initial_ready)
        predecessor_location = locations[predecessors[-1]] if predecessors else current_state.location_id
        blocked = any(status[item] in (FeasibilityStatus.BLOCKED, FeasibilityStatus.INFEASIBLE) for item in predecessors)
        start_at = end_at = ready_at = cutoff_at = None
        slack_sec = None
        origin_id = destination_id = None
        reasons: tuple[DomainReasonCode, ...] = ()
        item_status = FeasibilityStatus.FEASIBLE
        if blocked:
            item_status = FeasibilityStatus.BLOCKED
            reasons = (DomainReasonCode.HARD_DEADLINE_MISSED,)
        elif activity.kind is ActivityKind.FIXED_TRANSPORT:
            service = services[activity.service_id]  # type: ignore[index]
            state = effective[service.id]
            origin_id, destination_id = service.origin_id, service.destination_id
            cutoff_at = state.effective_departure - timedelta(seconds=service.origin_allowance_sec)
            slack_sec = int((cutoff_at - predecessor_ready).total_seconds())
            checks.append(_check(f"constraint:{activity.id}:readiness", predecessor_ready <= cutoff_at,
                DomainReasonCode.HARD_CONSTRAINTS_PASS if predecessor_ready <= cutoff_at else DomainReasonCode.SERVICE_CUTOFF_MISSED,
                _timestamp(predecessor_ready), _timestamp(cutoff_at), (state.provenance_id,)))
            if predecessor_location != origin_id:
                item_status, reasons = FeasibilityStatus.BLOCKED, (DomainReasonCode.LOCATION_UNREACHABLE,)
            elif state.status.value == "cancelled":
                item_status, reasons = FeasibilityStatus.BLOCKED, (DomainReasonCode.SERVICE_CANCELLED,)
            elif predecessor_ready > cutoff_at:
                item_status, reasons = FeasibilityStatus.BLOCKED, (DomainReasonCode.SERVICE_CUTOFF_MISSED,)
            else:
                start_at, end_at, ready_at = state.effective_departure, state.effective_arrival, state.effective_arrival
        elif activity.kind is ActivityKind.FLEXIBLE_TRANSFER:
            transfer = transfers[activity.transfer_template_id]  # type: ignore[index]
            origin_id, destination_id = transfer.origin_id, transfer.destination_id
            start_at = max(predecessor_ready, transfer.window_start)
            end_at, ready_at = start_at + timedelta(seconds=transfer.duration_sec), start_at + timedelta(seconds=transfer.duration_sec)
            if predecessor_location != origin_id:
                item_status, reasons = FeasibilityStatus.BLOCKED, (DomainReasonCode.LOCATION_UNREACHABLE,)
            elif start_at > transfer.latest_start:
                item_status, reasons = FeasibilityStatus.BLOCKED, (DomainReasonCode.ACTIVITY_WINDOW_MISSED,)
            checks.append(_check(f"constraint:{activity.id}:window", start_at <= transfer.latest_start,
                DomainReasonCode.HARD_CONSTRAINTS_PASS if start_at <= transfer.latest_start else DomainReasonCode.ACTIVITY_WINDOW_MISSED,
                _timestamp(start_at), _timestamp(transfer.latest_start), (transfer.provenance_id,)))
        elif activity.kind is ActivityKind.PROCESSING:
            origin_id = destination_id = activity.location_id
            start_at = predecessor_ready
            end_at = ready_at = start_at + timedelta(seconds=activity.duration_sec or 0)
        elif activity.kind is ActivityKind.HOTEL_CHECKIN:
            origin_id = destination_id = activity.location_id
            start_at = max(predecessor_ready, activity.earliest_start)  # type: ignore[arg-type]
            end_at = ready_at = start_at + timedelta(seconds=activity.duration_sec or 0)
            cutoff_at = activity.latest_start
            slack_sec = int((cutoff_at - start_at).total_seconds())  # type: ignore[operator]
            passed = start_at <= cutoff_at
            checks.append(_check(f"constraint:{activity.id}:latest_start", passed,
                DomainReasonCode.HARD_CONSTRAINTS_PASS if passed else DomainReasonCode.ACTIVITY_WINDOW_MISSED,
                _timestamp(start_at), _timestamp(cutoff_at)))
            if predecessor_location != origin_id:
                item_status, reasons = FeasibilityStatus.BLOCKED, (DomainReasonCode.LOCATION_UNREACHABLE,)
            elif not passed:
                item_status, reasons = FeasibilityStatus.INFEASIBLE, (DomainReasonCode.ACTIVITY_WINDOW_MISSED,)
        else:
            origin_id = destination_id = activity.location_id
            # The commitment's scheduled start is fixed; readiness records actual arrival.
            start_at = end_at = activity.start_at
            ready_at = predecessor_ready
            cutoff_at = activity.start_at - timedelta(seconds=activity.readiness_allowance_sec or 0)
            slack_sec = int((cutoff_at - predecessor_ready).total_seconds())
            item_status = classify_slack(slack_sec, risk_threshold_sec)
            passed = slack_sec >= 0
            reasons = () if passed else (DomainReasonCode.HARD_DEADLINE_MISSED,)
            checks.append(_check(f"constraint:{activity.id}:arrival_deadline", passed,
                DomainReasonCode.HARD_CONSTRAINTS_PASS if passed else DomainReasonCode.HARD_DEADLINE_MISSED,
                _seconds(slack_sec), _seconds(0)))
            if predecessor_location != origin_id:
                item_status, reasons = FeasibilityStatus.BLOCKED, (DomainReasonCode.LOCATION_UNREACHABLE,)
        ready[activity_id] = ready_at or predecessor_ready
        locations[activity_id] = destination_id
        status[activity_id] = item_status
        results.append(EvaluatedActivity(activity_id=activity_id, kind=activity.kind, service_id=activity.service_id,
            transfer_template_id=activity.transfer_template_id, origin_id=origin_id, destination_id=destination_id,
            start_at=start_at, end_at=end_at, ready_at=ready_at, cutoff_at=cutoff_at, slack_sec=slack_sec,
            status=item_status, reason_codes=reasons, provenance_ids=tuple(item for item in (activity.provenance_id,) if item)))
    overall = FeasibilityStatus.INFEASIBLE if any(item.status in (FeasibilityStatus.INFEASIBLE, FeasibilityStatus.BLOCKED) for item in results) else FeasibilityStatus.AT_RISK if any(item.status is FeasibilityStatus.AT_RISK for item in results) else FeasibilityStatus.FEASIBLE
    return tuple(results), tuple(checks), overall
