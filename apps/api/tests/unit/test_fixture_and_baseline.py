from resilitrip.application.snapshots import baseline_snapshot


def test_t01_fixture_loads_with_resolved_references(hero_fixture) -> None:
    assert hero_fixture.scenario.id == "mumbai-goa-v2"
    assert hero_fixture.catalog.catalog_version == "catalog:mumbai-goa-v2"
    assert len(hero_fixture.catalog.locations) == 7
    assert len(hero_fixture.catalog.services) == 4
    assert len(hero_fixture.original_itinerary.activities) == 6


def test_t02_connected_journey_projection_matches_dependency_chain(hero_fixture) -> None:
    snapshot = baseline_snapshot(hero_fixture)
    activity_ids = [activity.activity_id for activity in snapshot.evaluated_itinerary]
    assert activity_ids == ["act:T1", "act:T1-exit", "act:C1", "act:H1", "act:C2", "act:E1"]
    assert [(item.from_id, item.to_id) for item in snapshot.trip.active_itinerary.dependencies] == [
        ("act:T1", "act:T1-exit"), ("act:T1-exit", "act:C1"), ("act:C1", "act:H1"),
        ("act:H1", "act:C2"), ("act:C2", "act:E1"),
    ]


def test_t03_baseline_snapshot_matches_document_04(hero_fixture) -> None:
    snapshot = baseline_snapshot(hero_fixture)
    event = next(activity for activity in snapshot.evaluated_itinerary if activity.activity_id == "act:E1")
    assert event.start_at.isoformat() == "2026-09-26T19:30:00+05:30"
    assert event.cutoff_at.isoformat() == "2026-09-26T19:15:00+05:30"
    assert event.slack_sec == 5_100
    assert snapshot.overall_status.value == "feasible"
    assert next(activity for activity in snapshot.evaluated_itinerary if activity.activity_id == "act:C2").end_at.isoformat() == "2026-09-26T17:50:00+05:30"
