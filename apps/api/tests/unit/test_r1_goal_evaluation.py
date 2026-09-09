from datetime import datetime, timezone

from resilitrip.application.snapshots import create_initial_trip
from resilitrip.domain.events import apply_timing_event
from resilitrip.domain.goal_evaluation import (
    EvaluationReasonCode,
    FactKnowledge,
    GenericGoal,
    GoalFact,
    GoalKind,
    GoalRequirementStrength,
    ProcessCutoffRule,
    StructuralEvaluationInput,
    StructuralOutcome,
    evaluate_structurally,
)
from resilitrip.domain.models import TRUTH_LABEL
from resilitrip.domain.planner import plan_recovery


UTC = timezone.utc


def at(hour: int, minute: int = 0) -> datetime:
    return datetime(2026, 9, 26, hour, minute, tzinfo=UTC)


def goal(requirement=GoalRequirementStrength.HARD, target_at=at(12)) -> GenericGoal:
    return GenericGoal(id="goal:arrival", kind=GoalKind.ARRIVAL, requirement=requirement, label="Reach venue", target_at=target_at)


def evaluation(fact: GoalFact, *, current_goal=None, cutoff=None):
    return evaluate_structurally(StructuralEvaluationInput(goals=(current_goal or goal(),), facts=(fact,), process_cutoffs=() if cutoff is None else (cutoff,)))


def test_r1_fixed_process_cutoff_never_moves_for_late_fact():
    rule = ProcessCutoffRule(id="cutoff:checkin", goal_id="goal:arrival", fixed_cutoff_at=at(11), required_processing_sec=1_800)
    result = evaluation(GoalFact(id="fact:late", goal_id="goal:arrival", knowledge=FactKnowledge.KNOWN, available_at=at(10, 45)), cutoff=rule)
    assert rule.fixed_cutoff_at == at(11)
    assert rule.required_start_at == at(10, 30)
    assert result.outcome is StructuralOutcome.KNOWN_INFEASIBLE
    assert result.reasons[0].code is EvaluationReasonCode.PROCESSING_DEADLINE_MISSED


def test_r1_missing_hard_facts_are_conditional_not_feasible():
    result = evaluation(GoalFact(id="fact:unknown", goal_id="goal:arrival", knowledge=FactKnowledge.UNKNOWN))
    assert result.outcome is StructuralOutcome.MISSING_FACTS
    assert [reason.code for reason in result.reasons] == [EvaluationReasonCode.REQUIRED_FACT_UNKNOWN]


def test_r1_known_lower_bound_violation_is_infeasible():
    result = evaluation(GoalFact(id="fact:bound", goal_id="goal:arrival", knowledge=FactKnowledge.KNOWN, lower_bound_at=at(12, 1)))
    assert result.outcome is StructuralOutcome.KNOWN_INFEASIBLE
    assert result.reasons[0].code is EvaluationReasonCode.GOAL_LOWER_BOUND_MISSED


def test_r1_soft_goal_does_not_block_valid_structure():
    soft_goal = goal(requirement=GoalRequirementStrength.SOFT, target_at=at(12))
    result = evaluation(GoalFact(id="fact:soft", goal_id="goal:arrival", knowledge=FactKnowledge.KNOWN, available_at=at(12, 1)), current_goal=soft_goal)
    assert result.outcome is StructuralOutcome.VALID
    assert result.reasons[0].code is EvaluationReasonCode.SOFT_GOAL_UNMET


def test_r1_goal_evaluation_does_not_change_mumbai_goa_demo(hero_fixture):
    trip = apply_timing_event(create_initial_trip(hero_fixture), hero_fixture.replay_events[0])
    plans = {plan.id.split(":")[1]: plan for plan in plan_recovery(trip, hero_fixture.catalog).feasible_plans}
    assert trip.truth_label == TRUTH_LABEL
    assert {code: (plan.cash_required_paise, plan.incremental_cost_paise) for code, plan in plans.items()} == {
        "F2": (970_000, 840_000), "F3": (650_000, 520_000),
    }
