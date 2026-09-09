import pytest
from pydantic import ValidationError

from resilitrip.application.snapshots import create_initial_trip
from resilitrip.domain.models import TRUTH_LABEL, TripLifecycle


def test_r1_demo_trip_defaults_to_active_lifecycle(hero_fixture):
    trip = create_initial_trip(hero_fixture)
    assert trip.mode.value == "demo"
    assert trip.lifecycle is TripLifecycle.ACTIVE


@pytest.mark.parametrize(
    ("mode", "lifecycle", "truth_label", "message"),
    [
        ("real", "draft", TRUTH_LABEL, "real trips"),
        ("demo", "draft", TRUTH_LABEL, "demo trips must remain active"),
        ("demo", "active", "REAL TRIP", "synthetic/not-bookable"),
    ],
)
def test_r1_rejects_invalid_mode_lifecycle_or_truth_label_combinations(hero_fixture, mode, lifecycle, truth_label, message):
    trip = create_initial_trip(hero_fixture)
    with pytest.raises(ValidationError, match=message):
        trip.model_validate({
            **trip.model_dump(mode="json"), "mode": mode,
            "lifecycle": lifecycle, "truth_label": truth_label,
        })
