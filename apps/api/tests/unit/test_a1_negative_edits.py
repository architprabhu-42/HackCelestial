from copy import deepcopy

import pytest
from pydantic import ValidationError

from resilitrip.api.contracts import ConstraintsReplaceCommand
from resilitrip.domain.editing import validate_itinerary_replacement
from resilitrip.domain.models import CurrentState, TravelerPhase


def replacement(hero_fixture, **changes):
    return hero_fixture.original_itinerary.model_copy(update=changes)


def test_neg16_completed_activity_immutable(hero_fixture):
    state = hero_fixture.current_state.model_copy(update={"completed_activity_ids": ("act:R1",)})
    changed = replacement(hero_fixture, activities=hero_fixture.original_itinerary.activities[1:])
    with pytest.raises(ValueError, match="COMPLETED_ACTIVITY_IMMUTABLE"):
        validate_itinerary_replacement(hero_fixture.original_itinerary, changed, state, acknowledge_hard_removal=True)


def test_neg17_active_service_immutable(hero_fixture):
    state = CurrentState(as_of=hero_fixture.current_state.as_of, location_id=None, phase=TravelerPhase.ONBOARD,
        active_service_id="svc:T1:2026-09-26", completed_activity_ids=(), next_recovery_point_id="rail:MAO", provenance_id=hero_fixture.current_state.provenance_id)
    changed = replacement(hero_fixture, activities=tuple(a for a in hero_fixture.original_itinerary.activities if a.id != "act:T1"))
    with pytest.raises(ValueError, match="ACTIVE_ACTIVITY_IMMUTABLE"):
        validate_itinerary_replacement(hero_fixture.original_itinerary, changed, state, acknowledge_hard_removal=True)


def test_neg18_hard_removal_requires_acknowledgement(hero_fixture):
    changed = replacement(hero_fixture, activities=tuple(a for a in hero_fixture.original_itinerary.activities if a.id != "act:H1"))
    with pytest.raises(ValueError, match="HARD_CHANGE_ACKNOWLEDGEMENT_REQUIRED"):
        validate_itinerary_replacement(hero_fixture.original_itinerary, changed, hero_fixture.current_state, acknowledge_hard_removal=False)


def test_neg19_dependency_commitment_order_mismatch(hero_fixture):
    deps = hero_fixture.original_itinerary.dependencies
    changed = replacement(hero_fixture, dependencies=deps + (deps[0].model_copy(update={"id": "dep:bad", "from_id": "act:E1", "to_id": "act:R1"}),))
    with pytest.raises(Exception):
        validate_itinerary_replacement(hero_fixture.original_itinerary, changed, hero_fixture.current_state, acknowledge_hard_removal=True)


def test_neg20_catalog_service_time_is_immutable(hero_fixture):
    service = hero_fixture.catalog.services[0]
    with pytest.raises(ValidationError):
        service.scheduled_departure = service.scheduled_arrival


def test_neg21_missing_full_replacement_field_rejected(hero_fixture):
    with pytest.raises(ValidationError):
        ConstraintsReplaceCommand.model_validate({"expected_trip_version": 1, "constraints": hero_fixture.constraints.model_dump(mode="json")})
