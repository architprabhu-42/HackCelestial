"""Integration coverage for the isolated append-only generic R1 namespace."""

from datetime import date, datetime, timezone
import hashlib

import pytest
from pydantic import ValidationError

from resilitrip.application.snapshots import create_initial_trip
from resilitrip.domain.composed_evaluation import GenericCompositionInput
from resilitrip.domain.generic_trip import GenericTripAggregate
from resilitrip.domain.goal_evaluation import (
    FactKnowledge, GenericGoal, GoalFact, GoalKind, GoalRequirementStrength,
    StructuralEvaluationInput,
)
from resilitrip.domain.models import TRUTH_LABEL, evidence_value
from resilitrip.domain.events import apply_timing_event
from resilitrip.domain.planner import plan_recovery
from resilitrip.domain.primitives import CoverageState, EvidenceFact, ExactMoneyAmount, MoneyFact, MoneyScope, MoneyTiming
from resilitrip.domain.semantic_snapshots import EvaluationSnapshotHistory, SemanticAlternativePlan, append_snapshot, create_evaluation_snapshot
from resilitrip.domain.service_timing import DatedServiceRun, GenericServiceTiming, OrderedStopCall, ServiceCalendar, ServicePattern, UnknownObservedTimestamp, Weekday
from resilitrip.domain.topology import GenericPlace, GenericTransportMode, GenericTripTopology, PhysicalRouteSegment, PlaceInputType
from resilitrip.infrastructure.repositories import GenericTripRepository, canonical_json, content_hash
from resilitrip.infrastructure.sqlite import connect, initialize


UTC = timezone.utc


def at(hour: int) -> datetime:
    return datetime(2026, 9, 25, hour, tzinfo=UTC)


def generic_input() -> GenericCompositionInput:
    origin = GenericPlace(id="place:origin", label="Origin", input_type=PlaceInputType.MANUAL)
    destination = GenericPlace(id="place:destination", label="Destination", input_type=PlaceInputType.UNKNOWN)
    topology = GenericTripTopology(
        id="topology:real", places=(origin, destination),
        route_segments=(PhysicalRouteSegment(id="segment:rail", origin_place_id=origin.id, destination_place_id=destination.id, mode=GenericTransportMode.RAIL),),
        semantic_items=(), semantic_dependencies=(),
    )
    unknown = UnknownObservedTimestamp(observation_kind="unknown")
    run = DatedServiceRun(
        id="run:real", pattern_id="pattern:real", service_date=date(2026, 9, 25),
        stop_calls=(
            OrderedStopCall(id="call:origin", sequence=1, place_id=origin.id, scheduled_arrival_at=None, scheduled_departure_at=at(9), observed_arrival=unknown, observed_departure=unknown),
            OrderedStopCall(id="call:destination", sequence=2, place_id=destination.id, scheduled_arrival_at=at(11), scheduled_departure_at=None, observed_arrival=unknown, observed_departure=unknown),
        ),
    )
    timing = GenericServiceTiming(
        id="timing:real", places=(origin, destination), calendars=(ServiceCalendar(id="calendar:real", active_weekdays=(Weekday.FRIDAY,)),), calendar_exceptions=(),
        patterns=(ServicePattern(id="pattern:real", label="Manual rail", calendar_id="calendar:real", mode=GenericTransportMode.RAIL),), runs=(run,),
    )
    goal = GenericGoal(id="goal:arrival", kind=GoalKind.ARRIVAL, requirement=GoalRequirementStrength.HARD, label="Arrive", target_at=at(12))
    evidence = EvidenceFact(id="evidence:manual", provenance_id="source:manual", observed_at=at(8), coverage=CoverageState.MANUAL, value=evidence_value("text", "confirmed"))
    money = MoneyFact(id="money:cash", amount=ExactMoneyAmount(amount_kind="exact", paise=12_000), party_id="party:traveler", party_label="Traveller", scope=MoneyScope.PER_TRAVELER, timing=MoneyTiming.CASH_REQUIRED_NOW, description="Known cash due")
    return GenericCompositionInput(
        topology=topology, service_timing=timing,
        goal_evaluation=StructuralEvaluationInput(goals=(goal,), facts=(GoalFact(id="fact:arrival", goal_id=goal.id, knowledge=FactKnowledge.KNOWN, available_at=at(11)),)),
        evidence=(evidence,), required_evidence_ids=(evidence.id,), money=(money,),
    )


def semantic_snapshot(version: int, revision: int):
    value = generic_input()
    alternative = SemanticAlternativePlan(
        semantic_id="alternative:rail", revision=revision, topology_id=value.topology.id,
        timing_id=value.service_timing.id, goal_ids=("goal:arrival",), evidence_ids=("evidence:manual",), evaluation_status="feasible",
    )
    return create_evaluation_snapshot(
        snapshot_id=f"snapshot:{version}", trip_id="trip:generic-real", trip_version=version,
        created_at=at(12 + version), evaluation_input=value, alternatives=(alternative,),
    )


def aggregate(version: int = 1, history: EvaluationSnapshotHistory | None = None) -> GenericTripAggregate:
    return GenericTripAggregate(
        id="trip:generic-real", version=version, mode="real", lifecycle="draft",
        truth_label="REAL TRIP — FACTS MAY BE UNKNOWN", evaluation_input=generic_input(),
        semantic_snapshots=history or EvaluationSnapshotHistory(),
    )


def test_r1_generic_real_aggregate_persists_and_reloads(tmp_path) -> None:
    database_path = tmp_path / "generic.sqlite3"
    initialize(database_path)
    expected = aggregate(history=EvaluationSnapshotHistory(snapshots=(semantic_snapshot(1, 1),)))
    with connect(database_path) as connection:
        repository = GenericTripRepository(connection)
        repository.create_initial(expected)
        loaded = repository.get_current(expected.id)

    assert loaded == expected
    assert str(loaded.mode) == "real"
    assert str(loaded.lifecycle) == "draft"
    assert loaded.scenario_id is None


def test_r1_generic_trip_history_and_semantic_history_are_append_only(tmp_path) -> None:
    database_path = tmp_path / "history.sqlite3"
    initialize(database_path)
    first = semantic_snapshot(1, 1)
    initial = aggregate(history=EvaluationSnapshotHistory(snapshots=(first,)))
    second = semantic_snapshot(2, 2)
    updated = aggregate(version=2, history=append_snapshot(initial.semantic_snapshots, second))
    with connect(database_path) as connection:
        repository = GenericTripRepository(connection)
        repository.create_initial(initial)
        repository.save_version(1, updated)
        reloaded_initial = repository.get_version(initial.id, 1)
        history_rows = connection.execute("SELECT version FROM generic_trip_versions WHERE trip_id=? ORDER BY version", (initial.id,)).fetchall()
        semantic_rows = connection.execute("SELECT snapshot_id FROM generic_semantic_snapshots WHERE trip_id=? ORDER BY rowid", (initial.id,)).fetchall()

    assert history_rows == [(1,), (2,)]
    assert semantic_rows == [("snapshot:1",), ("snapshot:2",)]
    assert reloaded_initial == initial


def test_r1_generic_trip_rejects_stale_writes(tmp_path) -> None:
    database_path = tmp_path / "stale.sqlite3"
    initialize(database_path)
    initial = aggregate()
    updated = aggregate(version=2)
    with connect(database_path) as connection:
        repository = GenericTripRepository(connection)
        repository.create_initial(initial)
        repository.save_version(1, updated)
        with pytest.raises(ValueError, match="VERSION_CONFLICT"):
            repository.save_version(1, updated)


def test_r1_generic_semantic_snapshot_hash_corruption_is_rejected_before_parsing(tmp_path) -> None:
    database_path = tmp_path / "corrupt.sqlite3"
    initialize(database_path)
    expected = aggregate(history=EvaluationSnapshotHistory(snapshots=(semantic_snapshot(1, 1),)))
    with connect(database_path) as connection:
        repository = GenericTripRepository(connection)
        repository.create_initial(expected)
        connection.execute("UPDATE generic_semantic_snapshots SET snapshot_hash='corrupt' WHERE trip_id=?", (expected.id,))
        with pytest.raises(RuntimeError, match="INTERNAL_DATA_INTEGRITY_ERROR"):
            repository.get_semantic_history(expected.id)


def test_r1_generic_real_rejects_demo_identity_and_truth_label() -> None:
    with pytest.raises(ValidationError, match="scenario identity"):
        GenericTripAggregate.model_validate({**aggregate().model_dump(mode="json"), "scenario_id": "scenario:mumbai-goa"})
    with pytest.raises(ValidationError, match="synthetic demo truth label"):
        GenericTripAggregate.model_validate({**aggregate().model_dump(mode="json"), "truth_label": TRUTH_LABEL})


def test_r1_generic_migration_leaves_existing_demo_snapshot_and_hash_unchanged(tmp_path, hero_fixture) -> None:
    database_path = tmp_path / "legacy-demo.sqlite3"
    trip = create_initial_trip(hero_fixture)
    payload = canonical_json(trip.model_dump(mode="json"))
    digest = content_hash(trip.model_dump(mode="json"))
    with connect(database_path) as connection:
        connection.execute("CREATE TABLE schema_migrations (revision TEXT PRIMARY KEY, applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)")
        connection.executemany("INSERT INTO schema_migrations (revision) VALUES (?)", [("a1_initial_schema",), ("a3_backend_schema",), ("r1_trip_mode_namespace",), ("r1_trip_lifecycle",)])
        connection.execute("CREATE TABLE trips (trip_id TEXT PRIMARY KEY, current_version INTEGER NOT NULL, catalog_version TEXT NOT NULL, scenario_id TEXT NOT NULL, trip_mode TEXT NOT NULL, trip_lifecycle TEXT NOT NULL)")
        connection.execute("CREATE TABLE trip_versions (trip_id TEXT NOT NULL, version INTEGER NOT NULL, snapshot_json TEXT NOT NULL, snapshot_hash TEXT NOT NULL, mutation_kind TEXT NOT NULL, PRIMARY KEY(trip_id, version))")
        connection.execute("INSERT INTO trips VALUES (?,?,?,?,?,?)", (trip.id, trip.version, trip.catalog_version, trip.scenario_id, "demo", "active"))
        connection.execute("INSERT INTO trip_versions VALUES (?,?,?,?,?)", (trip.id, trip.version, payload, digest, "created"))

    initialize(database_path)
    with connect(database_path) as connection:
        preserved = connection.execute("SELECT snapshot_json,snapshot_hash FROM trip_versions WHERE trip_id=?", (trip.id,)).fetchone()
        generic_tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'generic_%'")}

    assert preserved == (payload, digest)
    assert generic_tables == {"generic_trips", "generic_trip_versions", "generic_semantic_snapshots"}


def test_r1_generic_namespace_does_not_change_mumbai_goa_demo_plans(hero_fixture) -> None:
    trip = apply_timing_event(create_initial_trip(hero_fixture), hero_fixture.replay_events[0])
    plans = {plan.id.split(":")[1]: plan for plan in plan_recovery(trip, hero_fixture.catalog).feasible_plans}

    assert trip.truth_label == TRUTH_LABEL
    assert {code: (plan.cash_required_paise, plan.incremental_cost_paise) for code, plan in plans.items()} == {
        "F2": (970_000, 840_000), "F3": (650_000, 520_000),
    }
