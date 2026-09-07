import hashlib
from pathlib import Path

from resilitrip.application.snapshots import create_initial_trip
from resilitrip.domain.events import apply_timing_event, calculate_impacts, evaluate_trip
from resilitrip.infrastructure.repositories import canonical_json
from resilitrip.domain.models import D1GoldenOutput


def test_t04_d1_applies_once_without_mutating_catalog(hero_fixture):
    baseline = create_initial_trip(hero_fixture)
    event = hero_fixture.replay_events[0]
    catalog_before = hashlib.sha256(canonical_json(hero_fixture.catalog.model_dump(mode="json")).encode()).hexdigest()
    after = apply_timing_event(baseline, event)
    assert after.version == 2
    t1 = next(item for item in after.effective_services if item.service_id == event.service_id)
    assert t1.effective_departure == event.new_departure_at
    assert t1.effective_arrival == event.new_arrival_at
    assert [item for item in after.effective_services if item.service_id != event.service_id] == [item for item in baseline.effective_services if item.service_id != event.service_id]
    assert catalog_before == hashlib.sha256(canonical_json(hero_fixture.catalog.model_dump(mode="json")).encode()).hexdigest()


def test_t05_d1_causal_impact_and_shared_evaluator(hero_fixture):
    baseline = create_initial_trip(hero_fixture)
    event = hero_fixture.replay_events[0]
    after = apply_timing_event(baseline, event)
    activities, _, overall = evaluate_trip(after, hero_fixture.catalog, evaluation_mode="current")
    values = {item.activity_id: item for item in activities}
    assert values["act:E1"].ready_at.isoformat() == "2026-09-26T20:50:00+05:30"
    assert values["act:E1"].slack_sec == -5700
    assert values["act:H1"].start_at.isoformat() == "2026-09-26T20:00:00+05:30"
    assert values["act:H1"].status.value == "feasible"
    assert overall.value == "infeasible"
    wedding = next(item for item in calculate_impacts(baseline, after, hero_fixture.catalog, event) if item.activity_id == "act:E1")
    assert wedding.root_event_ids == ("event:D1",)
    assert wedding.causal_activity_path == ("act:T1", "act:T1-exit", "act:C1", "act:H1", "act:C2", "act:E1")
    assert wedding.before_slack_sec == 5100
    assert wedding.after_slack_sec == -5700


def test_d1_golden_is_complete_schema_valid_evaluator_output(hero_fixture):
    golden_path = Path(__file__).parents[4] / "data" / "golden" / "d1.impact.json"
    golden = D1GoldenOutput.model_validate_json(golden_path.read_text(encoding="utf-8"))
    baseline = create_initial_trip(hero_fixture)
    event = hero_fixture.replay_events[0]
    after = apply_timing_event(baseline, event)
    activities, checks, overall = evaluate_trip(after, hero_fixture.catalog, evaluation_mode="current")
    expected = D1GoldenOutput(trip_version=2, catalog_version=after.catalog_version, event_id="event:D1",
        evaluated_itinerary=activities, constraint_checks=checks, overall_status=overall,
        impacts=calculate_impacts(baseline, after, hero_fixture.catalog, event))
    assert golden == expected
