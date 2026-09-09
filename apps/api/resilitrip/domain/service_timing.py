"""Generic service-pattern, calendar, run, and timing primitives.

These provider-independent structures do not describe availability, fares, seats,
accessibility, delays, or any demo catalog service.  Observed timestamps are
explicitly known or unknown rather than inferred from schedules.
"""

from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum
from typing import Annotated, Literal

from pydantic import Field, model_validator
from typing_extensions import TypeAliasType

from resilitrip.domain.models import ContractModel, DisplayLabel, EntityId
from resilitrip.domain.topology import GenericPlace, GenericTransportMode


class Weekday(StrEnum):
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


class CalendarExceptionType(StrEnum):
    ADDED = "added"
    REMOVED = "removed"


class ServiceCalendar(ContractModel):
    id: EntityId
    active_weekdays: tuple[Weekday, ...]

    @model_validator(mode="after")
    def weekday_entries_are_unique(self) -> "ServiceCalendar":
        if len(self.active_weekdays) != len(set(self.active_weekdays)):
            raise ValueError("calendar weekdays must be unique")
        return self


class CalendarException(ContractModel):
    id: EntityId
    calendar_id: EntityId
    service_date: date
    exception_type: CalendarExceptionType


class ServicePattern(ContractModel):
    id: EntityId
    label: DisplayLabel
    calendar_id: EntityId
    mode: GenericTransportMode


class KnownObservedTimestamp(ContractModel):
    observation_kind: Literal["known"]
    at: datetime


class UnknownObservedTimestamp(ContractModel):
    observation_kind: Literal["unknown"]


ObservedTimestamp = TypeAliasType(
    "ObservedTimestamp",
    Annotated[
        KnownObservedTimestamp | UnknownObservedTimestamp,
        Field(discriminator="observation_kind"),
    ],
)


class OrderedStopCall(ContractModel):
    id: EntityId
    sequence: Annotated[int, Field(strict=True, ge=1)]
    place_id: EntityId
    scheduled_arrival_at: datetime | None
    scheduled_departure_at: datetime | None
    observed_arrival: ObservedTimestamp
    observed_departure: ObservedTimestamp

    @model_validator(mode="after")
    def stop_timestamps_are_chronological(self) -> "OrderedStopCall":
        if self.scheduled_arrival_at is not None and self.scheduled_departure_at is not None and self.scheduled_departure_at < self.scheduled_arrival_at:
            raise ValueError("scheduled departure must not precede scheduled arrival")
        if isinstance(self.observed_arrival, KnownObservedTimestamp) and isinstance(self.observed_departure, KnownObservedTimestamp) and self.observed_departure.at < self.observed_arrival.at:
            raise ValueError("observed departure must not precede observed arrival")
        return self


class DatedServiceRun(ContractModel):
    id: EntityId
    pattern_id: EntityId
    service_date: date
    stop_calls: tuple[OrderedStopCall, ...]

    @model_validator(mode="after")
    def calls_are_ordered_and_chronological(self) -> "DatedServiceRun":
        if len(self.stop_calls) < 2:
            raise ValueError("a service run requires at least two stop calls")
        if [call.sequence for call in self.stop_calls] != list(range(1, len(self.stop_calls) + 1)):
            raise ValueError("stop calls must use contiguous declared order")
        if self.stop_calls[0].scheduled_departure_at is None or self.stop_calls[-1].scheduled_arrival_at is None:
            raise ValueError("a run requires first departure and final arrival schedules")
        for call in self.stop_calls[1:-1]:
            if call.scheduled_arrival_at is None or call.scheduled_departure_at is None:
                raise ValueError("intermediate stop calls require arrival and departure schedules")
        for previous, following in zip(self.stop_calls, self.stop_calls[1:]):
            if previous.scheduled_departure_at is None or following.scheduled_arrival_at is None:
                raise ValueError("adjacent stop calls require travel timestamps")
            if following.scheduled_arrival_at < previous.scheduled_departure_at:
                raise ValueError("service run travel must be chronological")
        return self


class GenericServiceTiming(ContractModel):
    """Generic service topology with explicit calendar and observation semantics."""

    id: EntityId
    places: tuple[GenericPlace, ...]
    calendars: tuple[ServiceCalendar, ...]
    calendar_exceptions: tuple[CalendarException, ...]
    patterns: tuple[ServicePattern, ...]
    runs: tuple[DatedServiceRun, ...]

    @model_validator(mode="after")
    def valid_references_and_calendars(self) -> "GenericServiceTiming":
        collections = (self.places, self.calendars, self.calendar_exceptions, self.patterns, self.runs)
        identifiers = [self.id, *(entry.id for collection in collections for entry in collection), *(call.id for run in self.runs for call in run.stop_calls)]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("service timing identifiers must be unique")

        calendar_by_id = {calendar.id: calendar for calendar in self.calendars}
        exception_by_calendar_date: dict[tuple[str, date], CalendarException] = {}
        for exception in self.calendar_exceptions:
            if exception.calendar_id not in calendar_by_id:
                raise ValueError("calendar exception reference does not resolve")
            key = (exception.calendar_id, exception.service_date)
            if key in exception_by_calendar_date:
                raise ValueError("calendar exceptions must be unique per date")
            exception_by_calendar_date[key] = exception

        pattern_by_id = {pattern.id: pattern for pattern in self.patterns}
        for pattern in self.patterns:
            if pattern.calendar_id not in calendar_by_id:
                raise ValueError("service pattern calendar reference does not resolve")

        place_ids = {place.id for place in self.places}
        weekday_values = tuple(Weekday)
        for run in self.runs:
            pattern = pattern_by_id.get(run.pattern_id)
            if pattern is None:
                raise ValueError("service run pattern reference does not resolve")
            if any(call.place_id not in place_ids for call in run.stop_calls):
                raise ValueError("stop call place reference does not resolve")
            calendar = calendar_by_id[pattern.calendar_id]
            exception = exception_by_calendar_date.get((calendar.id, run.service_date))
            scheduled = weekday_values[run.service_date.weekday()] in calendar.active_weekdays
            if exception is not None:
                scheduled = exception.exception_type is CalendarExceptionType.ADDED
            if not scheduled:
                raise ValueError("service run date is not active in its calendar")
        return self
