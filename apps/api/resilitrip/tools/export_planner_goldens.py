"""Generate deterministic Gate A2 planner goldens from the real fixture and domain planner."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from resilitrip.application.snapshots import create_initial_trip
from resilitrip.domain.events import apply_timing_event
from resilitrip.domain.models import RankingPreset
from resilitrip.domain.planner import plan_recovery, replace_constraints
from resilitrip.infrastructure.fixture_loader import load_fixture


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture-root", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    fixture = load_fixture(args.fixture_root)
    trip = apply_timing_event(create_initial_trip(fixture), fixture.replay_events[0])
    outputs = {
        "plans.cheapest.json": plan_recovery(trip, fixture.catalog, ranking_preset=RankingPreset.CHEAPEST),
        "plans.fastest.json": plan_recovery(trip, fixture.catalog, ranking_preset=RankingPreset.FASTEST),
        "plans.fewest-changes.json": plan_recovery(trip, fixture.catalog, ranking_preset=RankingPreset.FEWEST_CHANGES),
    }
    for limit, filename in ((700_000, "budget-7000.plans.json"), (500_000, "budget-5000.no-plan.json")):
        branch = replace_constraints(trip, trip.constraints.model_copy(update={"max_cash_required_paise": limit}))
        outputs[filename] = plan_recovery(branch, fixture.catalog)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for filename, result in outputs.items():
        (args.output_dir / filename).write_text(
            json.dumps(result.model_dump(mode="json"), sort_keys=True, indent=2) + "\n", encoding="utf-8"
        )


if __name__ == "__main__":
    main()
