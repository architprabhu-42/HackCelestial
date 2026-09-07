from datetime import timedelta

import pytest

from resilitrip.application.snapshots import create_initial_trip
from resilitrip.domain.events import apply_timing_event, evaluate_trip, replace_service_state
from resilitrip.domain.models import CurrentState, FeasibilityStatus, PlannerResultStatus, RankingPreset, ServiceStatus, TravelerPhase
from resilitrip.domain.planner import plan_adoptability, plan_recovery, replace_constraints


def d1(hero_fixture):
    return apply_timing_event(create_initial_trip(hero_fixture), hero_fixture.replay_events[0])


def with_service(catalog, service_id, **updates):
    services = tuple(item.model_copy(update=updates) if item.id == service_id else item for item in catalog.services)
    return catalog.model_copy(update={"services": services})


def plan_map(result):
    return {item.id.split(":")[1]: item for item in (*result.feasible_plans, *result.uncertain_plans, *result.rejected_plans)}


@pytest.mark.parametrize("preset,expected", [
    (RankingPreset.CHEAPEST, ["F3", "F2"]),
    (RankingPreset.FASTEST, ["F2", "F3"]),
    (RankingPreset.FEWEST_CHANGES, ["F3", "F2"]),
])
def test_t08_complete_hero_frontier_and_ranking(hero_fixture, preset, expected):
    result = plan_recovery(d1(hero_fixture), hero_fixture.catalog, ranking_preset=preset)
    assert result.result_status is PlannerResultStatus.COMPLETE
    assert result.search_complete
    assert [item.id.split(":")[1] for item in result.feasible_plans] == expected
    plans = plan_map(result)
    assert set(plans) == {"F2", "F3", "F4", "WAIT-T1"}
    assert plans["F4"].reason_codes == ("HARD_DEADLINE_MISSED",)
    assert plans["WAIT-T1"].reason_codes == ("HARD_DEADLINE_MISSED",)


def test_t09_fx01_7000_budget_leaves_only_f3(hero_fixture):
    trip = d1(hero_fixture)
    trip = replace_constraints(trip, trip.constraints.model_copy(update={"max_cash_required_paise": 700_000}))
    result = plan_recovery(trip, hero_fixture.catalog)
    assert [item.id.split(":")[1] for item in result.feasible_plans] == ["F3"]
    assert "CASH_LIMIT_EXCEEDED" in plan_map(result)["F2"].reason_codes


def test_t10_fx02_5000_budget_is_complete_no_plan(hero_fixture):
    trip = d1(hero_fixture)
    trip = replace_constraints(trip, trip.constraints.model_copy(update={"max_cash_required_paise": 500_000}))
    result = plan_recovery(trip, hero_fixture.catalog)
    assert result.result_status is PlannerResultStatus.NO_FEASIBLE_CATALOG_PLAN
    assert result.search_complete and not result.feasible_plans
    assert result.counts.rejected_total == 4


def test_t11_fx03_cancel_f3(hero_fixture):
    trip = replace_service_state(d1(hero_fixture), "svc:F3:2026-09-26", status=ServiceStatus.CANCELLED)
    result = plan_recovery(trip, hero_fixture.catalog)
    assert [item.id.split(":")[1] for item in result.feasible_plans] == ["F2"]
    assert result.counts.pruned_by_reason == {"SERVICE_CANCELLED": 1}


@pytest.mark.parametrize("departure,arrival,status,venue,slack", [
    ("2026-09-26T15:40:00+05:30", "2026-09-26T16:55:00+05:30", FeasibilityStatus.AT_RISK, "2026-09-26T19:00:00+05:30", 900),
    ("2026-09-26T15:56:00+05:30", "2026-09-26T17:11:00+05:30", FeasibilityStatus.INFEASIBLE, "2026-09-26T19:16:00+05:30", -60),
])
def test_t11_fx04_fx05_f3_timing(hero_fixture, departure, arrival, status, venue, slack):
    from datetime import datetime
    trip = replace_service_state(d1(hero_fixture), "svc:F3:2026-09-26", departure_at=datetime.fromisoformat(departure), arrival_at=datetime.fromisoformat(arrival), status=ServiceStatus.DELAYED)
    plan = plan_map(plan_recovery(trip, hero_fixture.catalog))["F3"]
    assert plan.evaluation_status is status
    assert plan.final_required_arrival_at.isoformat() == venue
    assert plan.event_slack_sec == slack


def test_t11_fx06_cancel_original_t1_keeps_flights(hero_fixture):
    baseline = replace_service_state(create_initial_trip(hero_fixture), "svc:T1:2026-09-26", status=ServiceStatus.CANCELLED)
    _, _, original_status = evaluate_trip(baseline, hero_fixture.catalog, evaluation_mode="current")
    result = plan_recovery(baseline, hero_fixture.catalog)
    assert original_status is FeasibilityStatus.INFEASIBLE
    assert [item.id.split(":")[1] for item in result.feasible_plans] == ["F3", "F2"]


def test_t11_fx07_capacity_zero(hero_fixture):
    catalog = with_service(hero_fixture.catalog, "svc:F3:2026-09-26", capacity=0)
    result = plan_recovery(d1(hero_fixture), catalog)
    assert [item.id.split(":")[1] for item in result.feasible_plans] == ["F2"]
    assert "CAPACITY_INSUFFICIENT" in plan_map(result)["F3"].reason_codes


def test_t11_fx08_capacity_unknown(hero_fixture):
    catalog = with_service(hero_fixture.catalog, "svc:F3:2026-09-26", capacity=None)
    result = plan_recovery(d1(hero_fixture), catalog)
    assert [item.id.split(":")[1] for item in result.feasible_plans] == ["F2"]
    assert [item.id.split(":")[1] for item in result.uncertain_plans] == ["F3"]
    assert "CAPACITY_UNKNOWN" in result.uncertain_plans[0].reason_codes


def test_t11_fx09_accessibility_unknown_needs_input(hero_fixture):
    trip = d1(hero_fixture)
    trip = replace_constraints(trip, trip.constraints.model_copy(update={"accessibility_required": True}))
    result = plan_recovery(trip, hero_fixture.catalog)
    assert result.result_status is PlannerResultStatus.NEEDS_INPUT
    assert not result.feasible_plans
    assert {item.id.split(":")[1] for item in result.uncertain_plans} == {"F2", "F3"}


def test_t11_fx10_validity_is_exclusive(hero_fixture):
    result = plan_recovery(d1(hero_fixture), hero_fixture.catalog)
    f3 = plan_map(result)["F3"]
    assert plan_adoptability(f3, f3.valid_until - timedelta(seconds=1), search_complete=True) == (True, None)
    assert plan_adoptability(f3, f3.valid_until, search_complete=True)[1].value == "STALE_PLAN"


def test_t11_fx11_invalid_onboard_state_needs_input(hero_fixture):
    trip = d1(hero_fixture)
    state = CurrentState(as_of=trip.current_state.as_of, location_id=None, phase=TravelerPhase.ONBOARD,
        active_service_id="svc:T1:2026-09-26", completed_activity_ids=(), next_recovery_point_id=None,
        provenance_id=trip.current_state.provenance_id)
    result = plan_recovery(trip.model_copy(update={"current_state": state}), hero_fixture.catalog)
    assert result.result_status is PlannerResultStatus.NEEDS_INPUT
    assert result.counts.pruned_by_reason == {"UNSUPPORTED_CURRENT_STATE": 1}
    assert not result.feasible_plans


def test_fx12_duplicate_event_is_idempotent(hero_fixture):
    baseline = create_initial_trip(hero_fixture)
    after = apply_timing_event(baseline, hero_fixture.replay_events[0])
    duplicate = apply_timing_event(after, hero_fixture.replay_events[0])
    assert duplicate == after and duplicate.version == 2


def test_fx13_event_id_conflict(hero_fixture):
    baseline = create_initial_trip(hero_fixture)
    after = apply_timing_event(baseline, hero_fixture.replay_events[0])
    conflicting = hero_fixture.replay_events[0].model_copy(update={"new_arrival_at": hero_fixture.replay_events[0].new_arrival_at + timedelta(minutes=1)})
    with pytest.raises(ValueError, match="EVENT_ID_CONFLICT"):
        apply_timing_event(after, conflicting)


def test_fx14_stale_event_version(hero_fixture):
    after = d1(hero_fixture)
    stale = hero_fixture.replay_events[0].model_copy(update={"event_id": "event:stale"})
    with pytest.raises(ValueError, match="VERSION_CONFLICT"):
        apply_timing_event(after, stale)


def test_t11_fx15_partial_search_is_not_ranked_or_adoptable(hero_fixture):
    result = plan_recovery(d1(hero_fixture), hero_fixture.catalog, interrupt_before_search=True)
    assert result.result_status is PlannerResultStatus.PARTIAL_SEARCH
    assert not result.search_complete and not result.feasible_plans
    normal = plan_recovery(d1(hero_fixture), hero_fixture.catalog).feasible_plans[0]
    assert plan_adoptability(normal, d1(hero_fixture).current_state.as_of, search_complete=False)[0] is False


def test_t12_exact_money_reconciliation(hero_fixture):
    plans = plan_map(plan_recovery(d1(hero_fixture), hero_fixture.catalog))
    assert {code: (plan.cash_required_paise, plan.incremental_cost_paise) for code, plan in plans.items()} == {
        "F2": (970_000, 840_000), "F3": (650_000, 520_000),
        "F4": (570_000, 440_000), "WAIT-T1": (130_000, 0),
    }
    assert [item.id for item in plans["F2"].money_items] == ["money:F2:X1", "money:F2:fare", "money:F2:GOX-hotel", "money:F2:C2"]
    assert [item.id for item in plans["F3"].money_items] == ["money:F3:X1", "money:F3:fare", "money:F3:GOI-hotel", "money:F3:C2"]
    assert [item.id for item in plans["F4"].money_items] == ["money:F4:X1", "money:F4:fare", "money:F4:GOX-hotel", "money:F4:C2"]
    assert [item.id for item in plans["WAIT-T1"].money_items] == ["money:C1-due", "money:C2-due"]
    assert all(plan.potential_refund_paise is None for plan in plans.values())
    assert all(len({item.id for item in plan.money_items}) == len(plan.money_items) for plan in plans.values())
