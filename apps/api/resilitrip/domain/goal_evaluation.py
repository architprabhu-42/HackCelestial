"""Generic goals, fixed process cutoffs, and structural evaluation primitives.

This is deliberately independent from the Mumbai--Goa fixture and evaluator.
It does not calculate slack, search alternatives, or infer missing facts.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from enum import StrEnum

from pydantic import Field, model_validator

from resilitrip.domain.models import ContractModel, DisplayLabel, EntityId, PositiveDurationSec


class GoalKind(StrEnum):
    ARRIVAL = "arrival"
    STAY = "stay"
    ACTIVITY = "activity"
    DEADLINE = "deadline"
    FREE_TIME = "free_time"


class GoalRequirementStrength(StrEnum):
    HARD = "hard"
    SOFT = "soft"


class FactKnowledge(StrEnum):
    KNOWN = "known"
    UNKNOWN = "unknown"


class StructuralOutcome(StrEnum):
    VALID = "valid"
    MISSING_FACTS = "missing_facts"
    KNOWN_INFEASIBLE = "known_infeasible"


class EvaluationReasonCode(StrEnum):
    REQUIRED_FACT_UNKNOWN = "required_fact_unknown"
    SOFT_FACT_UNKNOWN = "soft_fact_unknown"
    GOAL_TARGET_MISSED = "goal_target_missed"
    GOAL_LOWER_BOUND_MISSED = "goal_lower_bound_missed"
    SOFT_GOAL_UNMET = "soft_goal_unmet"
    PROCESSING_DEADLINE_MISSED = "processing_deadline_missed"
    PROCESSING_LOWER_BOUND_MISSED = "processing_lower_bound_missed"


class GenericGoal(ContractModel):
    id: EntityId
    kind: GoalKind
    requirement: GoalRequirementStrength
    label: DisplayLabel
    target_at: datetime | None = None


class GoalFact(ContractModel):
    """Known timing evidence or an explicit unknown; no estimate is fabricated."""

    id: EntityId
    goal_id: EntityId
    knowledge: FactKnowledge
    available_at: datetime | None = None
    lower_bound_at: datetime | None = None

    @model_validator(mode="after")
    def fact_knowledge_is_explicit(self) -> "GoalFact":
        if self.knowledge is FactKnowledge.UNKNOWN and (self.available_at is not None or self.lower_bound_at is not None):
            raise ValueError("unknown facts must not contain timestamps")
        if self.knowledge is FactKnowledge.KNOWN and self.available_at is None and self.lower_bound_at is None:
            raise ValueError("known facts require available_at or lower_bound_at")
        if self.available_at is not None and self.lower_bound_at is not None and self.lower_bound_at > self.available_at:
            raise ValueError("lower_bound_at must not follow available_at")
        return self


class ProcessCutoffRule(ContractModel):
    """A fixed cutoff and required processing time, deliberately not a slack value."""

    id: EntityId
    goal_id: EntityId
    fixed_cutoff_at: datetime
    required_processing_sec: PositiveDurationSec

    @property
    def required_start_at(self) -> datetime:
        return self.fixed_cutoff_at - timedelta(seconds=self.required_processing_sec)


class StructuralEvaluationInput(ContractModel):
    goals: tuple[GenericGoal, ...]
    facts: tuple[GoalFact, ...]
    process_cutoffs: tuple[ProcessCutoffRule, ...] = ()

    @model_validator(mode="after")
    def references_and_ids_are_valid(self) -> "StructuralEvaluationInput":
        identifiers = [*(goal.id for goal in self.goals), *(fact.id for fact in self.facts), *(rule.id for rule in self.process_cutoffs)]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("structural evaluation identifiers must be unique")
        goal_ids = {goal.id for goal in self.goals}
        if any(fact.goal_id not in goal_ids for fact in self.facts):
            raise ValueError("goal fact reference does not resolve")
        if any(rule.goal_id not in goal_ids for rule in self.process_cutoffs):
            raise ValueError("process cutoff goal reference does not resolve")
        if len({fact.goal_id for fact in self.facts}) != len(self.facts):
            raise ValueError("each goal may have only one structural fact")
        if len({rule.goal_id for rule in self.process_cutoffs}) != len(self.process_cutoffs):
            raise ValueError("each goal may have only one process cutoff")
        return self


class StructuralReason(ContractModel):
    goal_id: EntityId
    code: EvaluationReasonCode


class StructuralEvaluation(ContractModel):
    outcome: StructuralOutcome
    reasons: tuple[StructuralReason, ...]


def evaluate_structurally(value: StructuralEvaluationInput) -> StructuralEvaluation:
    """Evaluate only known structural facts; unknown required evidence is conditional."""
    facts = {fact.goal_id: fact for fact in value.facts}
    cutoffs = {rule.goal_id: rule for rule in value.process_cutoffs}
    infeasible: list[StructuralReason] = []
    missing: list[StructuralReason] = []
    advisory: list[StructuralReason] = []

    def reason_for(goal: GenericGoal, code: EvaluationReasonCode) -> None:
        target = advisory if goal.requirement is GoalRequirementStrength.SOFT else infeasible
        target.append(StructuralReason(goal_id=goal.id, code=code))

    for goal in value.goals:
        fact = facts.get(goal.id)
        if fact is None or fact.knowledge is FactKnowledge.UNKNOWN:
            if goal.requirement is GoalRequirementStrength.HARD:
                missing.append(StructuralReason(goal_id=goal.id, code=EvaluationReasonCode.REQUIRED_FACT_UNKNOWN))
            else:
                advisory.append(StructuralReason(goal_id=goal.id, code=EvaluationReasonCode.SOFT_FACT_UNKNOWN))
            continue
        if goal.target_at is not None:
            if fact.lower_bound_at is not None and fact.lower_bound_at > goal.target_at:
                reason_for(goal, EvaluationReasonCode.GOAL_LOWER_BOUND_MISSED)
            elif fact.available_at is not None and fact.available_at > goal.target_at:
                reason_for(goal, EvaluationReasonCode.GOAL_TARGET_MISSED if goal.requirement is GoalRequirementStrength.HARD else EvaluationReasonCode.SOFT_GOAL_UNMET)
        cutoff = cutoffs.get(goal.id)
        if cutoff is not None:
            # The fixed cutoff is never adjusted for a late/observed availability fact.
            if fact.lower_bound_at is not None and fact.lower_bound_at > cutoff.required_start_at:
                reason_for(goal, EvaluationReasonCode.PROCESSING_LOWER_BOUND_MISSED)
            elif fact.available_at is not None and fact.available_at > cutoff.required_start_at:
                reason_for(goal, EvaluationReasonCode.PROCESSING_DEADLINE_MISSED)

    if infeasible:
        return StructuralEvaluation(outcome=StructuralOutcome.KNOWN_INFEASIBLE, reasons=tuple(infeasible + missing + advisory))
    if missing:
        return StructuralEvaluation(outcome=StructuralOutcome.MISSING_FACTS, reasons=tuple(missing + advisory))
    return StructuralEvaluation(outcome=StructuralOutcome.VALID, reasons=tuple(advisory))
