import json
from copy import deepcopy

import pytest
from pydantic import ValidationError

from resilitrip.domain.models import ExecutableScenarioFixture
from resilitrip.domain.validation import DomainValidationError, validate_fixture


def load_mutated(repository_root, mutator):
    payload = json.loads((repository_root / "data" / "fixtures" / "mumbai-goa-v2.json").read_text(encoding="utf-8"))
    mutator(payload)
    return ExecutableScenarioFixture.model_validate_json(json.dumps(payload))


@pytest.mark.parametrize(
    ("negative_id", "mutator", "schema_failure"),
    [
        ("NEG-01", lambda value: value["catalog"]["services"][0].__setitem__("scheduled_departure", "2026-09-26T06:00:00"), True),
        ("NEG-02", lambda value: value["catalog"]["locations"].append(deepcopy(value["catalog"]["locations"][0])), False),
        ("NEG-03", lambda value: value["original_itinerary"]["dependencies"].append({"id":"dep:E1-to-T1","from_id":"act:E1","to_id":"act:T1","buffer_sec":0,"reason":"invalid_cycle"}), False),
        ("NEG-04", lambda value: value["catalog"]["transfer_templates"][0].__setitem__("policy_id", "policy:missing"), False),
        ("NEG-05", lambda value: value["catalog"]["transfer_templates"][0].__setitem__("duration_sec", 0), True),
        ("NEG-06", lambda value: value["catalog"]["services"][0].__setitem__("capacity", -1), True),
        ("NEG-07", lambda value: value["catalog"]["services"][0].__setitem__("scheduled_arrival", "2026-09-26T05:59:00+05:30"), True),
        ("NEG-08", lambda value: value["baseline_money_items"][0].__setitem__("amount_paise", True), True),
        ("NEG-09", lambda value: value["constraints"].__setitem__("party_size", 2), True),
        ("NEG-10", lambda value: value.__setitem__("bookable", True), True),
        ("NEG-11", lambda value: value["original_itinerary"]["activities"][3].update({"earliest_start":"2026-09-26T22:00:00+05:30","latest_start":"2026-09-26T21:00:00+05:30"}), True),
        ("NEG-12", lambda value: value["baseline_money_items"].append(deepcopy(value["baseline_money_items"][0])), False),
        ("NEG-13", lambda value: value["original_itinerary"]["activities"][2].__setitem__("transfer_template_id", "xfer:X-GOX-HOTEL"), False),
        ("NEG-14", lambda value: value["current_state"].update({"phase":"onboard","location_id":None,"active_service_id":None}), True),
        ("NEG-15", lambda value: value["replay_events"][0].__setitem__("type", "WEATHER_UPDATED"), True),
    ],
)
def test_neg_01_through_neg_15(repository_root, negative_id, mutator, schema_failure) -> None:
    if schema_failure:
        with pytest.raises(ValidationError):
            load_mutated(repository_root, mutator)
        return
    fixture = load_mutated(repository_root, mutator)
    with pytest.raises(DomainValidationError):
        validate_fixture(fixture)
