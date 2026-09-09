from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from resilitrip.domain.events import apply_timing_event
from resilitrip.domain.models import TRUTH_LABEL, evidence_value
from resilitrip.domain.planner import plan_recovery
from resilitrip.domain.primitives import (
    CoverageState,
    EvidenceFact,
    ExactMoneyAmount,
    MoneyFact,
    MoneyScope,
    MoneyTiming,
    RangeMoneyAmount,
    UnknownMoneyAmount,
)
from resilitrip.application.snapshots import create_initial_trip


OBSERVED = datetime(2026, 9, 26, 8, 0, tzinfo=timezone.utc)


def fact(coverage: CoverageState, value=None, **updates) -> EvidenceFact:
    values = {
        "id": "fact:fare", "provenance_id": "source:manual", "observed_at": OBSERVED,
        "coverage": coverage,
        "value": evidence_value("unknown", None) if value is None else value,
    }
    values.update(updates)
    return EvidenceFact(**values)


def test_r1_coverage_states_and_explicit_unknown_facts():
    for state in CoverageState:
        observed = fact(state, evidence_value("integer", 4) if state is CoverageState.MANUAL else None)
        assert observed.coverage is state
    assert fact(CoverageState.SUPPORTED).value.value_kind == "unknown"


@pytest.mark.parametrize("coverage", [
    CoverageState.NOT_COVERED,
    CoverageState.TEMPORARILY_UNAVAILABLE,
    CoverageState.UNKNOWN,
])
def test_r1_unavailable_coverage_cannot_invent_a_value(coverage):
    with pytest.raises(ValidationError, match="explicit unknown"):
        fact(coverage, evidence_value("integer", 4))


def test_r1_evidence_rejects_invalid_or_naive_timestamps():
    with pytest.raises(ValidationError, match="fresh_until"):
        fact(CoverageState.SUPPORTED, fresh_until=OBSERVED.replace(hour=7))
    with pytest.raises(ValidationError, match="timezone"):
        fact(CoverageState.SUPPORTED, observed_at=datetime(2026, 9, 26, 8, 0))


def test_r1_exact_range_and_unknown_money_preserve_metadata():
    exact = ExactMoneyAmount(amount_kind="exact", paise=12_345)
    amount_range = RangeMoneyAmount(amount_kind="range", minimum_paise=10_000, maximum_paise=15_000)
    unknown = UnknownMoneyAmount(amount_kind="unknown")
    statement = MoneyFact(
        id="money:cash", amount=exact, party_id="party:two", party_label="Two travellers",
        scope=MoneyScope.PARTY_TOTAL, timing=MoneyTiming.CASH_REQUIRED_NOW,
        description="Pay the operator now",
    )
    assert (statement.amount, amount_range, unknown.amount_kind) == (exact, amount_range, "unknown")
    assert statement.timing is MoneyTiming.CASH_REQUIRED_NOW


def test_r1_money_rejects_inverted_ranges_and_does_not_coerce_unknown_to_zero():
    with pytest.raises(ValidationError, match="minimum_paise"):
        RangeMoneyAmount(amount_kind="range", minimum_paise=10, maximum_paise=9)
    unknown = MoneyFact(
        id="money:refund", amount=UnknownMoneyAmount(amount_kind="unknown"),
        party_id="party:one", party_label="Traveller", scope=MoneyScope.PER_TRAVELER,
        timing=MoneyTiming.UNRECEIVED_REFUND, description="Refund estimate unavailable",
    )
    assert unknown.amount.model_dump() == {"amount_kind": "unknown"}
    assert "paise" not in unknown.amount.model_dump()


def test_r1_primitives_do_not_change_mumbai_goa_demo_money_or_truth_label(hero_fixture):
    trip = apply_timing_event(create_initial_trip(hero_fixture), hero_fixture.replay_events[0])
    result = plan_recovery(trip, hero_fixture.catalog)
    plans = {
        plan.id.split(":")[1]: plan
        for plan in (*result.feasible_plans, *result.uncertain_plans, *result.rejected_plans)
    }
    assert trip.mode.value == "demo"
    assert trip.truth_label == TRUTH_LABEL
    assert {code: (plan.cash_required_paise, plan.incremental_cost_paise) for code, plan in plans.items()} == {
        "F2": (970_000, 840_000), "F3": (650_000, 520_000),
        "F4": (570_000, 440_000), "WAIT-T1": (130_000, 0),
    }
