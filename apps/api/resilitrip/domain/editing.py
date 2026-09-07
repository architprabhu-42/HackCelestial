"""Frozen-prefix validation for the future-itinerary replacement contract."""

from __future__ import annotations

from resilitrip.domain.models import CurrentState, ItineraryDefinition, TravelerPhase
from resilitrip.domain.validation import validate_dependency_dag
import networkx as nx


def validate_itinerary_replacement(
    original: ItineraryDefinition,
    replacement: ItineraryDefinition,
    current_state: CurrentState,
    *,
    acknowledge_hard_removal: bool,
    required_commitment_ids: tuple[str, ...] = (),
) -> None:
    old = {activity.id: activity for activity in original.activities}
    new = {activity.id: activity for activity in replacement.activities}
    frozen_ids = set(current_state.completed_activity_ids)
    if current_state.phase is TravelerPhase.ONBOARD:
        frozen_ids.update(
            activity.id for activity in original.activities if activity.service_id == current_state.active_service_id
        )
    for activity_id in frozen_ids:
        if activity_id not in new or new[activity_id] != old[activity_id]:
            raise ValueError("COMPLETED_ACTIVITY_IMMUTABLE" if activity_id in current_state.completed_activity_ids else "ACTIVE_ACTIVITY_IMMUTABLE")
    for activity in original.activities:
        if activity.hard and activity.id not in new and not acknowledge_hard_removal:
            raise ValueError("HARD_CHANGE_ACKNOWLEDGEMENT_REQUIRED")
    validate_dependency_dag(replacement)
    activity_ids = {activity.id for activity in replacement.activities}
    if any(item not in activity_ids for item in required_commitment_ids):
        raise ValueError("ITINERARY_EDIT_INVALID")
    graph = nx.DiGraph((edge.from_id, edge.to_id) for edge in replacement.dependencies)
    graph.add_nodes_from(activity_ids)
    for earlier, later in zip(required_commitment_ids, required_commitment_ids[1:]):
        if not nx.has_path(graph, earlier, later):
            raise ValueError("ITINERARY_EDIT_INVALID")
