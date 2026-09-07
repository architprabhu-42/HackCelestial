"""Baseline itinerary projection only; recovery planning is intentionally absent."""

from __future__ import annotations

from datetime import datetime, timedelta

import networkx as nx

from resilitrip.domain.models import (
    ActivityKind,
    EvaluatedActivity,
    ExecutableScenarioFixture,
    FeasibilityStatus,
)


def evaluate_baseline(fixture: ExecutableScenarioFixture) -> tuple[tuple[EvaluatedActivity, ...], FeasibilityStatus]:
    catalog = fixture.catalog
    services = {item.id: item for item in catalog.services}
    transfers = {item.id: item for item in catalog.transfer_templates}
    activities = {item.id: item for item in fixture.original_itinerary.activities}
    graph = nx.DiGraph()
    graph.add_nodes_from(activities)
    graph.add_edges_from((item.from_id, item.to_id) for item in fixture.original_itinerary.dependencies)
    order = list(nx.lexicographical_topological_sort(graph, key=lambda value: value))
    prior_end: dict[str, datetime] = {}
    result: list[EvaluatedActivity] = []
    overall = FeasibilityStatus.FEASIBLE

    for activity_id in order:
        activity = activities[activity_id]
        predecessor_ends = [prior_end[node] for node in graph.predecessors(activity_id)]
        predecessor_end = max(predecessor_ends) if predecessor_ends else fixture.current_state.as_of
        origin_id = destination_id = None
        service_id = activity.service_id
        transfer_id = activity.transfer_template_id
        cutoff_at = slack_sec = None
        if activity.kind is ActivityKind.FIXED_TRANSPORT:
            service = services[activity.service_id]  # type: ignore[index]
            start_at, end_at = service.scheduled_departure, service.scheduled_arrival
            origin_id, destination_id = service.origin_id, service.destination_id
            ready_at = start_at - timedelta(seconds=service.origin_allowance_sec)
        elif activity.kind is ActivityKind.FLEXIBLE_TRANSFER:
            transfer = transfers[activity.transfer_template_id]  # type: ignore[index]
            start_at = max(predecessor_end, transfer.window_start)
            end_at = start_at + timedelta(seconds=transfer.duration_sec)
            ready_at = end_at
            origin_id, destination_id = transfer.origin_id, transfer.destination_id
        elif activity.kind is ActivityKind.PROCESSING:
            start_at = predecessor_end
            end_at = start_at + timedelta(seconds=activity.duration_sec or 0)
            ready_at = end_at
            origin_id = destination_id = activity.location_id
        elif activity.kind is ActivityKind.HOTEL_CHECKIN:
            start_at = max(predecessor_end, activity.earliest_start)  # type: ignore[arg-type]
            end_at = start_at + timedelta(seconds=activity.duration_sec or 0)
            ready_at = end_at
            cutoff_at = activity.latest_start
            slack_sec = int((cutoff_at - start_at).total_seconds())  # type: ignore[operator]
            origin_id = destination_id = activity.location_id
        else:
            start_at = activity.start_at
            end_at = activity.start_at
            ready_at = activity.start_at
            cutoff_at = activity.start_at - timedelta(seconds=activity.readiness_allowance_sec or 0)
            slack_sec = int((cutoff_at - predecessor_end).total_seconds())
            origin_id = destination_id = activity.location_id
        status = FeasibilityStatus.FEASIBLE
        if slack_sec is not None and slack_sec < 0:
            status = FeasibilityStatus.INFEASIBLE
            overall = FeasibilityStatus.INFEASIBLE
        elif slack_sec is not None and slack_sec < fixture.constraints.risk_threshold_sec:
            status = FeasibilityStatus.AT_RISK
        prior_end[activity_id] = end_at  # type: ignore[assignment]
        result.append(EvaluatedActivity(
            activity_id=activity_id, kind=activity.kind, service_id=service_id,
            transfer_template_id=transfer_id, origin_id=origin_id, destination_id=destination_id,
            start_at=start_at, end_at=end_at, ready_at=ready_at, cutoff_at=cutoff_at,
            slack_sec=slack_sec, status=status, reason_codes=(),
            provenance_ids=tuple(item for item in (activity.provenance_id,) if item),
        ))
    return tuple(result), overall
