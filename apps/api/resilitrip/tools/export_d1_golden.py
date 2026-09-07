"""Create the proposed D1 golden strictly from the production evaluator."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from resilitrip.application.snapshots import create_initial_trip
from resilitrip.domain.events import apply_timing_event, calculate_impacts, evaluate_trip
from resilitrip.domain.models import D1GoldenOutput
from resilitrip.infrastructure.fixture_loader import load_fixture


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    fixture = load_fixture(args.fixture_root)
    before = create_initial_trip(fixture)
    event = fixture.replay_events[0]
    after = apply_timing_event(before, event)
    evaluated, checks, overall = evaluate_trip(after, fixture.catalog, evaluation_mode="current")
    golden = D1GoldenOutput(trip_version=2, catalog_version=after.catalog_version, event_id="event:D1",
        evaluated_itinerary=evaluated, constraint_checks=checks, overall_status=overall,
        impacts=calculate_impacts(before, after, fixture.catalog, event))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(golden.model_dump(mode="json"), sort_keys=True, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
