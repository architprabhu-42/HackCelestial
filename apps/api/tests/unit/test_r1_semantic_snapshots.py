from datetime import date, datetime, timezone

import pytest
from pydantic import ValidationError

from resilitrip.application.snapshots import create_initial_trip
from resilitrip.domain.composed_evaluation import GenericCompositionInput
from resilitrip.domain.events import apply_timing_event
from resilitrip.domain.goal_evaluation import FactKnowledge, GenericGoal, GoalFact, GoalKind, GoalRequirementStrength, StructuralEvaluationInput
from resilitrip.domain.models import TRUTH_LABEL, evidence_value
from resilitrip.domain.planner import plan_recovery
from resilitrip.domain.primitives import CoverageState, EvidenceFact
from resilitrip.domain.semantic_snapshots import EvaluationSnapshotHistory, SemanticAlternativePlan, append_snapshot, create_evaluation_snapshot
from resilitrip.domain.service_timing import DatedServiceRun, GenericServiceTiming, OrderedStopCall, ServiceCalendar, ServicePattern, UnknownObservedTimestamp, Weekday
from resilitrip.domain.topology import GenericPlace, GenericTransportMode, GenericTripTopology, PlaceInputType


UTC = timezone.utc


def at(hour: int) -> datetime:
    return datetime(2026, 9, 25, hour, tzinfo=UTC)


def composition_input() -> GenericCompositionInput:
    place = GenericPlace(id="place:one", label="Manual place", input_type=PlaceInputType.MANUAL)
    topology = GenericTripTopology(id="topology:one", places=(place,), route_segments=(), semantic_items=(), semantic_dependencies=())
    unknown = UnknownObservedTimestamp(observation_kind="unknown")
    calls = (
        OrderedStopCall(id="call:one", sequence=1, place_id=place.id, scheduled_arrival_at=None, scheduled_departure_at=at(9), observed_arrival=unknown, observed_departure=unknown),
        OrderedStopCall(id="call:two", sequence=2, place_id=place.id, scheduled_arrival_at=at(10), scheduled_departure_at=None, observed_arrival=unknown, observed_departure=unknown),
    )
    timing = GenericServiceTiming(id="timing:one", places=(place,), calendars=(ServiceCalendar(id="calendar:one", active_weekdays=(Weekday.FRIDAY,)),), calendar_exceptions=(), patterns=(ServicePattern(id="pattern:one", label="Manual run", calendar_id="calendar:one", mode=GenericTransportMode.RAIL),), runs=(DatedServiceRun(id="run:one", pattern_id="pattern:one", service_date=date(2026, 9, 25), stop_calls=calls),))
    goal = GenericGoal(id="goal:one", kind=GoalKind.ARRIVAL, requirement=GoalRequirementStrength.HARD, label="Arrive", target_at=at(11))
    evidence = EvidenceFact(id="evidence:one", provenance_id="source:manual", observed_at=at(8), coverage=CoverageState.MANUAL, value=evidence_value("text", "confirmed"))
    return GenericCompositionInput(topology=topology, service_timing=timing, goal_evaluation=StructuralEvaluationInput(goals=(goal,), facts=(GoalFact(id="fact:one", goal_id=goal.id, knowledge=FactKnowledge.KNOWN, available_at=at(10)),)), evidence=(evidence,), required_evidence_ids=(evidence.id,))


def alternative(semantic_id: str, revision: int) -> SemanticAlternativePlan:
    value = composition_input()
    return SemanticAlternativePlan(semantic_id=semantic_id, revision=revision, topology_id=value.topology.id, timing_id=value.service_timing.id, goal_ids=("goal:one",), evidence_ids=("evidence:one",), evaluation_status="feasible")


def snapshot(identifier: str, created_at: datetime, alternatives: tuple[SemanticAlternativePlan, ...]):
    return create_evaluation_snapshot(snapshot_id=identifier, trip_id="trip:real", trip_version=1, created_at=created_at, evaluation_input=composition_input(), alternatives=alternatives)


def test_r1_multiple_semantic_alternatives_and_revision_progression():
    first = snapshot("snapshot:one", at(12), (alternative("alternative:rail", 1), alternative("alternative:walk", 1)))
    second = snapshot("snapshot:two", at(13), (alternative("alternative:rail", 2), alternative("alternative:walk", 2)))
    history = EvaluationSnapshotHistory(snapshots=(first, second))
    assert [item.semantic_id for item in first.alternatives] == ["alternative:rail", "alternative:walk"]
    assert history.snapshots[1].alternatives[0].revision == 2
    with pytest.raises(ValidationError, match="revisions must progress"):
        EvaluationSnapshotHistory(snapshots=(first, snapshot("snapshot:bad", at(14), (alternative("alternative:rail", 4),))))


def test_r1_snapshots_are_immutable_and_prior_history_is_not_mutated():
    first = snapshot("snapshot:one", at(12), (alternative("alternative:rail", 1),))
    history = EvaluationSnapshotHistory(snapshots=(first,))
    with pytest.raises(ValidationError):
        first.trip_id = "trip:changed"
    updated = append_snapshot(history, snapshot("snapshot:two", at(13), (alternative("alternative:rail", 2),)))
    assert history.snapshots == (first,)
    assert len(updated.snapshots) == 2


def test_r1_snapshot_rejects_unresolved_alternative_references():
    invalid = alternative("alternative:rail", 1).model_copy(update={"topology_id": "topology:missing"})
    with pytest.raises(ValidationError, match="topology/timing reference"):
        snapshot("snapshot:invalid", at(12), (invalid,))


def test_r1_semantic_snapshots_do_not_change_mumbai_goa_demo(hero_fixture):
    trip = apply_timing_event(create_initial_trip(hero_fixture), hero_fixture.replay_events[0])
    plans = {plan.id.split(":")[1]: plan for plan in plan_recovery(trip, hero_fixture.catalog).feasible_plans}
    assert trip.truth_label == TRUTH_LABEL
    assert {code: (plan.cash_required_paise, plan.incremental_cost_paise) for code, plan in plans.items()} == {"F2": (970_000, 840_000), "F3": (650_000, 520_000)}
