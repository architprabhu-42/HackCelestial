from datetime import date, datetime, timezone

import pytest
from pydantic import ValidationError

from resilitrip.application.snapshots import create_initial_trip
from resilitrip.domain.events import apply_timing_event
from resilitrip.domain.models import TRUTH_LABEL
from resilitrip.domain.planner import plan_recovery
from resilitrip.domain.service_timing import (
    CalendarException,
    CalendarExceptionType,
    DatedServiceRun,
    GenericServiceTiming,
    KnownObservedTimestamp,
    OrderedStopCall,
    ServiceCalendar,
    ServicePattern,
    UnknownObservedTimestamp,
    Weekday,
)
from resilitrip.domain.topology import GenericPlace, GenericTransportMode, PlaceInputType


UTC = timezone.utc


def observed_unknown():
    return UnknownObservedTimestamp(observation_kind="unknown")


def call(identifier, sequence, place_id, arrival, departure):
    return OrderedStopCall(
        id=identifier, sequence=sequence, place_id=place_id,
        scheduled_arrival_at=arrival, scheduled_departure_at=departure,
        observed_arrival=observed_unknown(), observed_departure=observed_unknown(),
    )


def service_timing(**updates) -> GenericServiceTiming:
    overnight = DatedServiceRun(
        id="run:overnight", pattern_id="pattern:night", service_date=date(2026, 9, 25),
        stop_calls=(
            call("call:origin", 1, "place:origin", None, datetime(2026, 9, 25, 23, 30, tzinfo=UTC)),
            call("call:mid", 2, "place:mid", datetime(2026, 9, 26, 1, 0, tzinfo=UTC), datetime(2026, 9, 26, 1, 10, tzinfo=UTC)),
            call("call:destination", 3, "place:destination", datetime(2026, 9, 27, 0, 20, tzinfo=UTC), None),
        ),
    )
    values = {
        "id": "timing:weekend", "places": (
            GenericPlace(id="place:origin", label="Origin", input_type=PlaceInputType.MANUAL),
            GenericPlace(id="place:mid", label="Midpoint", input_type=PlaceInputType.UNKNOWN),
            GenericPlace(id="place:destination", label="Destination", input_type=PlaceInputType.MANUAL),
        ),
        "calendars": (ServiceCalendar(id="calendar:weekend", active_weekdays=(Weekday.FRIDAY,)),),
        "calendar_exceptions": (),
        "patterns": (ServicePattern(id="pattern:night", label="Night service", calendar_id="calendar:weekend", mode=GenericTransportMode.RAIL),),
        "runs": (overnight,),
    }
    values.update(updates)
    return GenericServiceTiming(**values)


def test_r1_calendars_and_exceptions_allow_added_and_reject_removed_runs():
    added = CalendarException(id="exception:add", calendar_id="calendar:weekend", service_date=date(2026, 9, 26), exception_type=CalendarExceptionType.ADDED)
    saturday_run = service_timing().runs[0].model_copy(update={"id": "run:added", "service_date": date(2026, 9, 26)})
    assert service_timing(calendar_exceptions=(added,), runs=(saturday_run,)).runs[0].service_date == date(2026, 9, 26)
    removed = CalendarException(id="exception:remove", calendar_id="calendar:weekend", service_date=date(2026, 9, 25), exception_type=CalendarExceptionType.REMOVED)
    with pytest.raises(ValidationError, match="not active"):
        service_timing(calendar_exceptions=(removed,))


def test_r1_overnight_multi_day_run_and_unknown_observations_are_explicit():
    run = service_timing().runs[0]
    assert run.stop_calls[-1].scheduled_arrival_at.date() == date(2026, 9, 27)
    assert run.stop_calls[1].observed_arrival.observation_kind == "unknown"
    known = KnownObservedTimestamp(observation_kind="known", at=datetime(2026, 9, 26, 1, 5, tzinfo=UTC))
    assert known.at.hour == 1


def test_r1_rejects_invalid_stop_order_chronology_and_known_references():
    unordered = service_timing().runs[0].model_copy(update={"stop_calls": (
        call("call:a", 1, "place:origin", None, datetime(2026, 9, 25, 23, 30, tzinfo=UTC)),
        call("call:b", 3, "place:destination", datetime(2026, 9, 26, 1, 0, tzinfo=UTC), None),
    )})
    with pytest.raises(ValidationError, match="contiguous declared order"):
        service_timing(runs=(unordered,))
    backwards = service_timing().runs[0].model_copy(update={"stop_calls": (
        call("call:a", 1, "place:origin", None, datetime(2026, 9, 25, 23, 30, tzinfo=UTC)),
        call("call:b", 2, "place:destination", datetime(2026, 9, 25, 23, 0, tzinfo=UTC), None),
    )})
    with pytest.raises(ValidationError, match="chronological"):
        service_timing(runs=(backwards,))
    dangling_pattern = service_timing().runs[0].model_copy(update={"pattern_id": "pattern:missing"})
    with pytest.raises(ValidationError, match="pattern reference"):
        service_timing(runs=(dangling_pattern,))
    dangling_place_call = service_timing().runs[0].stop_calls[1].model_copy(update={"place_id": "place:missing"})
    dangling_place_run = service_timing().runs[0].model_copy(update={"stop_calls": (
        service_timing().runs[0].stop_calls[0], dangling_place_call, service_timing().runs[0].stop_calls[2],
    )})
    with pytest.raises(ValidationError, match="place reference"):
        service_timing(runs=(dangling_place_run,))
    with pytest.raises(ValidationError, match="timezone"):
        call("call:naive", 1, "place:origin", None, datetime(2026, 9, 25, 23, 30))


def test_r1_service_timing_does_not_change_mumbai_goa_demo(hero_fixture):
    trip = apply_timing_event(create_initial_trip(hero_fixture), hero_fixture.replay_events[0])
    plans = {plan.id.split(":")[1]: plan for plan in plan_recovery(trip, hero_fixture.catalog).feasible_plans}
    assert trip.truth_label == TRUTH_LABEL
    assert {code: (plan.cash_required_paise, plan.incremental_cost_paise) for code, plan in plans.items()} == {
        "F2": (970_000, 840_000), "F3": (650_000, 520_000),
    }
