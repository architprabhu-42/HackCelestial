from datetime import timedelta

import pytest

from resilitrip.domain.constraints import (
    classify_slack, hotel_start_is_valid, meets_cutoff, money_within_limits,
    plan_is_valid, require_location_continuity, schedule_flexible_transfer,
    service_cutoff, validate_onboard_state,
)
from resilitrip.domain.models import FeasibilityStatus


def test_t06_exact_boundaries(hero_fixture):
    commitment = next(item for item in hero_fixture.original_itinerary.activities if item.id == "act:E1")
    hotel = next(item for item in hero_fixture.original_itinerary.activities if item.id == "act:H1")
    service = next(item for item in hero_fixture.catalog.services if item.id == "svc:F2:2026-09-26")
    cutoff = service_cutoff(service.scheduled_departure, service.origin_allowance_sec)
    assert classify_slack(0, 1800) is FeasibilityStatus.AT_RISK
    assert classify_slack(-1, 1800) is FeasibilityStatus.INFEASIBLE
    assert classify_slack(1800, 1800) is FeasibilityStatus.FEASIBLE
    assert classify_slack(1799, 1800) is FeasibilityStatus.AT_RISK
    assert meets_cutoff(cutoff, cutoff)
    assert not meets_cutoff(cutoff + timedelta(seconds=1), cutoff)
    assert hotel_start_is_valid(hotel.latest_start, hotel.latest_start)
    assert not hotel_start_is_valid(hotel.latest_start + timedelta(seconds=1), hotel.latest_start)
    assert money_within_limits(700000, 900000, 700000, 900000)
    assert not money_within_limits(700001, 900000, 700000, 900000)
    assert plan_is_valid(commitment.start_at - timedelta(seconds=1), commitment.start_at)
    assert not plan_is_valid(commitment.start_at, commitment.start_at)


def test_t07_location_windows_and_onboard_state(hero_fixture):
    transfer = next(item for item in hero_fixture.catalog.transfer_templates if item.id == "xfer:X-GOI-HOTEL")
    start, _ = schedule_flexible_transfer(transfer.window_start, transfer)
    assert start == transfer.window_start
    with pytest.raises(ValueError, match="ACTIVITY_WINDOW_MISSED"):
        schedule_flexible_transfer(transfer.latest_start + timedelta(seconds=1), transfer)
    with pytest.raises(ValueError, match="LOCATION_UNREACHABLE"):
        require_location_continuity("loc:GOI:T1", "loc:GOX")
    with pytest.raises(ValueError, match="UNSUPPORTED_CURRENT_STATE"):
        validate_onboard_state("svc:F2:2026-09-26", None, "airport:GOI:ARR")
    with pytest.raises(ValueError, match="UNSUPPORTED_CURRENT_STATE"):
        validate_onboard_state("svc:F2:2026-09-26", "rail:CSMT", "airport:GOI:ARR")
    assert validate_onboard_state("svc:F2:2026-09-26", "airport:GOI:ARR", "airport:GOI:ARR") == "airport:GOI:ARR"
