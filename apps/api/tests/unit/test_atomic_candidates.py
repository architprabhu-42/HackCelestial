from dataclasses import replace

from resilitrip.application.snapshots import create_initial_trip
from resilitrip.domain.events import apply_timing_event
from resilitrip.domain.models import ServiceCatalog
from resilitrip.domain.recovery import build_catalog_indexes, derive_recovery_frontier, enumerate_atomic_candidates


def after_d1(hero_fixture):
    return apply_timing_event(create_initial_trip(hero_fixture), hero_fixture.replay_events[0])


def test_recovery_frontier_is_hero_cstmt_at_0515(hero_fixture):
    frontier = derive_recovery_frontier(after_d1(hero_fixture))
    assert frontier.location_id == "rail:CSMT"
    assert frontier.decision_ready_at.isoformat() == "2026-09-26T05:15:00+05:30"
    assert frontier.required_obligation_ids == ("act:H1", "act:E1")


def test_atomic_candidates_use_fixture_records_and_shared_evaluator(hero_fixture):
    candidates = enumerate_atomic_candidates(after_d1(hero_fixture), hero_fixture.catalog)
    assert [(item.id, item.sequence) for item in candidates] == [
        ("plan:F2:v2", ("xfer:X1", "svc:F2:2026-09-26", "process:F2-exit", "xfer:X-GOX-HOTEL", "act:H1", "xfer:C2", "act:E1")),
        ("plan:F3:v2", ("xfer:X1", "svc:F3:2026-09-26", "process:F3-exit", "xfer:X-GOI-HOTEL", "act:H1", "xfer:C2", "act:E1")),
        ("plan:F4:v2", ("xfer:X1", "svc:F4:2026-09-26", "process:F4-exit", "xfer:X-GOX-HOTEL", "act:H1", "xfer:C2", "act:E1")),
        ("plan:WAIT-T1:v2", ("svc:T1:2026-09-26", "process:T1-exit", "xfer:C1", "act:H1", "xfer:C2", "act:E1")),
    ]
    assert {item.id for item in candidates if item.status.value == "infeasible"} == {"plan:F4:v2", "plan:WAIT-T1:v2"}
    assert all(len({a.service_id for a in item.itinerary.activities if a.service_id}) == len([a for a in item.itinerary.activities if a.service_id]) for item in candidates)
    assert all(item.status.value != "blocked" for item in candidates)  # no location teleportation is accepted


def test_shuffled_catalog_keeps_order_and_bounds(hero_fixture):
    trip = after_d1(hero_fixture)
    original = enumerate_atomic_candidates(trip, hero_fixture.catalog)
    catalog = hero_fixture.catalog.model_copy(update={"services": tuple(reversed(hero_fixture.catalog.services)), "transfer_templates": tuple(reversed(hero_fixture.catalog.transfer_templates))})
    shuffled = enumerate_atomic_candidates(trip, catalog)
    assert [(item.id, item.signature) for item in shuffled] == [(item.id, item.signature) for item in original]
    indexes = build_catalog_indexes(catalog, trip.effective_services)
    assert indexes.services_by_origin["airport:BOM:T2"] == ("svc:F2:2026-09-26", "svc:F3:2026-09-26", "svc:F4:2026-09-26")
    assert len(shuffled) == 4
    assert all(len(item.sequence) <= 20 for item in shuffled)
    assert all(sum(step.startswith("svc:") for step in item.sequence) <= trip.constraints.max_new_fixed_legs for item in shuffled)
    assert all(sum(step.startswith("xfer:") for step in item.sequence) <= trip.constraints.max_transfer_legs for item in shuffled)
