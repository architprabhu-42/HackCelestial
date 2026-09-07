from pathlib import Path

from resilitrip.application.snapshots import create_initial_trip
from resilitrip.domain.events import apply_timing_event
from resilitrip.domain.models import PlannerResult, RankingPreset
from resilitrip.domain.planner import plan_recovery, replace_constraints


def test_gate_a2_planner_goldens_are_schema_valid_real_outputs(hero_fixture):
    root = Path(__file__).parents[4] / "data" / "golden"
    trip = apply_timing_event(create_initial_trip(hero_fixture), hero_fixture.replay_events[0])
    expected = {
        "plans.cheapest.json": plan_recovery(trip, hero_fixture.catalog, ranking_preset=RankingPreset.CHEAPEST),
        "plans.fastest.json": plan_recovery(trip, hero_fixture.catalog, ranking_preset=RankingPreset.FASTEST),
        "plans.fewest-changes.json": plan_recovery(trip, hero_fixture.catalog, ranking_preset=RankingPreset.FEWEST_CHANGES),
    }
    for limit, filename in ((700_000, "budget-7000.plans.json"), (500_000, "budget-5000.no-plan.json")):
        branch = replace_constraints(trip, trip.constraints.model_copy(update={"max_cash_required_paise": limit}))
        expected[filename] = plan_recovery(branch, hero_fixture.catalog)
    for filename, generated in expected.items():
        committed = PlannerResult.model_validate_json((root / filename).read_text(encoding="utf-8"))
        assert committed == generated
