from datetime import date, datetime, timezone

from resilitrip.application.snapshots import create_initial_trip
from resilitrip.domain.composed_evaluation import (
    ComposedOutcome,
    CompositionReasonCode,
    GenericCompositionInput,
    compose_evaluation,
)
from resilitrip.domain.events import apply_timing_event
from resilitrip.domain.goal_evaluation import (
    FactKnowledge, GenericGoal, GoalFact, GoalKind, GoalRequirementStrength,
    StructuralEvaluationInput,
)
from resilitrip.domain.models import TRUTH_LABEL, evidence_value
from resilitrip.domain.planner import plan_recovery
from resilitrip.domain.primitives import (
    CoverageState, EvidenceFact, ExactMoneyAmount, MoneyFact, MoneyScope,
    MoneyTiming, UnknownMoneyAmount,
)
from resilitrip.domain.service_timing import (
    DatedServiceRun, GenericServiceTiming, OrderedStopCall, ServiceCalendar,
    ServicePattern, UnknownObservedTimestamp, Weekday,
)
from resilitrip.domain.topology import (
    GenericPlace, GenericTransportMode, GenericTripTopology, PhysicalRouteSegment,
    PlaceInputType,
)


UTC = timezone.utc


def at(hour: int) -> datetime:
    return datetime(2026, 9, 25, hour, tzinfo=UTC)


def unknown_observation():
    return UnknownObservedTimestamp(observation_kind="unknown")


def composition_input(**updates) -> GenericCompositionInput:
    origin = GenericPlace(id="place:origin", label="Origin", input_type=PlaceInputType.MANUAL)
    destination = GenericPlace(id="place:destination", label="Destination", input_type=PlaceInputType.UNKNOWN)
    topology = GenericTripTopology(id="topology:one", places=(origin, destination), route_segments=(PhysicalRouteSegment(id="route:one", origin_place_id=origin.id, destination_place_id=destination.id, mode=GenericTransportMode.RAIL),), semantic_items=(), semantic_dependencies=())
    calls = (
        OrderedStopCall(id="call:origin", sequence=1, place_id=origin.id, scheduled_arrival_at=None, scheduled_departure_at=at(9), observed_arrival=unknown_observation(), observed_departure=unknown_observation()),
        OrderedStopCall(id="call:destination", sequence=2, place_id=destination.id, scheduled_arrival_at=at(11), scheduled_departure_at=None, observed_arrival=unknown_observation(), observed_departure=unknown_observation()),
    )
    timing = GenericServiceTiming(id="timing:one", places=(origin, destination), calendars=(ServiceCalendar(id="calendar:one", active_weekdays=(Weekday.FRIDAY,)),), calendar_exceptions=(), patterns=(ServicePattern(id="pattern:one", label="Rail", calendar_id="calendar:one", mode=GenericTransportMode.RAIL),), runs=(DatedServiceRun(id="run:one", pattern_id="pattern:one", service_date=date(2026, 9, 25), stop_calls=calls),))
    goal = GenericGoal(id="goal:arrival", kind=GoalKind.ARRIVAL, requirement=GoalRequirementStrength.HARD, label="Arrive", target_at=at(12))
    goals = StructuralEvaluationInput(goals=(goal,), facts=(GoalFact(id="fact:goal", goal_id=goal.id, knowledge=FactKnowledge.KNOWN, available_at=at(11)),))
    evidence = EvidenceFact(id="evidence:route", provenance_id="source:manual", observed_at=at(8), coverage=CoverageState.MANUAL, value=evidence_value("text", "user confirmed"))
    money = (
        MoneyFact(id="money:sunk", amount=ExactMoneyAmount(amount_kind="exact", paise=10_000), party_id="party:one", party_label="Traveller", scope=MoneyScope.PER_TRAVELER, timing=MoneyTiming.SUNK_COST, description="Already paid"),
        MoneyFact(id="money:cash", amount=ExactMoneyAmount(amount_kind="exact", paise=20_000), party_id="party:one", party_label="Traveller", scope=MoneyScope.PER_TRAVELER, timing=MoneyTiming.CASH_REQUIRED_NOW, description="Pay now"),
        MoneyFact(id="money:refund", amount=ExactMoneyAmount(amount_kind="exact", paise=3_000), party_id="party:one", party_label="Traveller", scope=MoneyScope.PER_TRAVELER, timing=MoneyTiming.UNRECEIVED_REFUND, description="Refund pending"),
    )
    values = {"topology": topology, "service_timing": timing, "goal_evaluation": goals, "evidence": (evidence,), "required_evidence_ids": (evidence.id,), "money": money}
    values.update(updates)
    return GenericCompositionInput(**values)


def test_r1_composed_valid_result_preserves_evidence_and_money_buckets():
    result = compose_evaluation(composition_input())
    assert result.outcome is ComposedOutcome.FEASIBLE
    assert result.evidence_references[0].provenance_id == "source:manual"
    assert result.money.sunk_cost.paise == 10_000
    assert result.money.cash_due_now.paise == 20_000
    assert result.money.unreceived_refund.paise == 3_000


def test_r1_composed_unknown_required_evidence_is_not_feasible_or_zero():
    unknown = EvidenceFact(id="evidence:route", provenance_id="source:manual", observed_at=at(8), coverage=CoverageState.SUPPORTED, value=evidence_value("unknown", None))
    unknown_cash = MoneyFact(id="money:cash", amount=UnknownMoneyAmount(amount_kind="unknown"), party_id="party:one", party_label="Traveller", scope=MoneyScope.PER_TRAVELER, timing=MoneyTiming.CASH_REQUIRED_NOW, description="Unknown cash")
    result = compose_evaluation(composition_input(evidence=(unknown,), money=(unknown_cash,)))
    assert result.outcome is ComposedOutcome.MISSING_REQUIRED_FACTS
    assert any(reason.code is CompositionReasonCode.REQUIRED_EVIDENCE_UNKNOWN for reason in result.reasons)
    assert result.money.cash_due_now.amount_kind == "unknown"


def test_r1_composed_unknown_money_is_conditional_without_zero_coercion():
    unknown_cash = MoneyFact(id="money:cash", amount=UnknownMoneyAmount(amount_kind="unknown"), party_id="party:one", party_label="Traveller", scope=MoneyScope.PER_TRAVELER, timing=MoneyTiming.CASH_REQUIRED_NOW, description="Unknown cash")
    result = compose_evaluation(composition_input(money=(unknown_cash,)))
    assert result.outcome is ComposedOutcome.CONDITIONAL
    assert result.money.cash_due_now.amount_kind == "unknown"
    assert any(reason.code is CompositionReasonCode.MONEY_AMOUNT_UNKNOWN for reason in result.reasons)


def test_r1_composed_structural_error_and_known_infeasibility_are_distinct():
    invalid_place = GenericPlace(id="place:outside", label="Outside", input_type=PlaceInputType.MANUAL)
    source_timing = composition_input().service_timing
    invalid_calls = tuple(call.model_copy(update={"place_id": invalid_place.id}) for call in source_timing.runs[0].stop_calls)
    invalid_run = DatedServiceRun.model_validate({**source_timing.runs[0].model_dump(mode="json"), "stop_calls": invalid_calls})
    invalid_timing = GenericServiceTiming.model_validate({**source_timing.model_dump(mode="json"), "places": (invalid_place,), "runs": (invalid_run,)})
    assert compose_evaluation(composition_input(service_timing=invalid_timing)).outcome is ComposedOutcome.STRUCTURAL_ERROR
    impossible_goals = composition_input().goal_evaluation.model_copy(update={"facts": (GoalFact(id="fact:late", goal_id="goal:arrival", knowledge=FactKnowledge.KNOWN, lower_bound_at=at(13)),)})
    assert compose_evaluation(composition_input(goal_evaluation=impossible_goals)).outcome is ComposedOutcome.KNOWN_INFEASIBLE


def test_r1_composition_does_not_change_mumbai_goa_demo(hero_fixture):
    trip = apply_timing_event(create_initial_trip(hero_fixture), hero_fixture.replay_events[0])
    plans = {plan.id.split(":")[1]: plan for plan in plan_recovery(trip, hero_fixture.catalog).feasible_plans}
    assert trip.truth_label == TRUTH_LABEL
    assert {code: (plan.cash_required_paise, plan.incremental_cost_paise) for code, plan in plans.items()} == {"F2": (970_000, 840_000), "F3": (650_000, 520_000)}
