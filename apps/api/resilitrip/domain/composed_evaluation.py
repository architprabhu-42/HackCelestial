"""Pure composition of the isolated R1 generic domain primitives.

No ranking, search, provider call, persistence, API, or demo behavior belongs in
this module.  It only composes known structural inputs into an honest result.
"""

from __future__ import annotations

from enum import StrEnum

from resilitrip.domain.goal_evaluation import (
    StructuralEvaluation,
    StructuralEvaluationInput,
    StructuralOutcome,
    evaluate_structurally,
)
from resilitrip.domain.models import ContractModel, EntityId, UnknownEvidenceValue
from resilitrip.domain.primitives import (
    CoverageState,
    EvidenceFact,
    ExactMoneyAmount,
    MoneyAmount,
    MoneyFact,
    MoneyTiming,
    RangeMoneyAmount,
    UnknownMoneyAmount,
)
from resilitrip.domain.service_timing import GenericServiceTiming
from resilitrip.domain.topology import GenericTripTopology


class ComposedOutcome(StrEnum):
    STRUCTURAL_ERROR = "structural_error"
    MISSING_REQUIRED_FACTS = "missing_required_facts"
    KNOWN_INFEASIBLE = "known_infeasible"
    CONDITIONAL = "conditional"
    FEASIBLE = "feasible"


class CompositionReasonCode(StrEnum):
    TIMING_PLACE_NOT_IN_TOPOLOGY = "timing_place_not_in_topology"
    REQUIRED_EVIDENCE_MISSING = "required_evidence_missing"
    REQUIRED_EVIDENCE_UNKNOWN = "required_evidence_unknown"
    MONEY_AMOUNT_UNKNOWN = "money_amount_unknown"
    MONEY_AMOUNT_RANGE = "money_amount_range"


class CompositionReason(ContractModel):
    code: CompositionReasonCode
    reference_id: EntityId


class EvidenceReference(ContractModel):
    fact_id: EntityId
    provenance_id: EntityId
    coverage: CoverageState


class ComposedMoney(ContractModel):
    sunk_cost: MoneyAmount
    cash_due_now: MoneyAmount
    unreceived_refund: MoneyAmount


class GenericCompositionInput(ContractModel):
    topology: GenericTripTopology
    service_timing: GenericServiceTiming
    goal_evaluation: StructuralEvaluationInput
    evidence: tuple[EvidenceFact, ...]
    required_evidence_ids: tuple[EntityId, ...] = ()
    money: tuple[MoneyFact, ...] = ()


class GenericCompositionResult(ContractModel):
    outcome: ComposedOutcome
    reasons: tuple[CompositionReason, ...]
    goal_evaluation: StructuralEvaluation
    evidence_references: tuple[EvidenceReference, ...]
    money: ComposedMoney


def _sum_money(items: tuple[MoneyFact, ...]) -> MoneyAmount:
    if any(isinstance(item.amount, UnknownMoneyAmount) for item in items):
        return UnknownMoneyAmount(amount_kind="unknown")
    minimum = 0
    maximum = 0
    ranged = False
    for item in items:
        if isinstance(item.amount, ExactMoneyAmount):
            minimum += item.amount.paise
            maximum += item.amount.paise
        else:
            assert isinstance(item.amount, RangeMoneyAmount)
            minimum += item.amount.minimum_paise
            maximum += item.amount.maximum_paise
            ranged = True
    if ranged:
        return RangeMoneyAmount(amount_kind="range", minimum_paise=minimum, maximum_paise=maximum)
    return ExactMoneyAmount(amount_kind="exact", paise=minimum)


def compose_evaluation(value: GenericCompositionInput) -> GenericCompositionResult:
    """Compose the generic R1 slices; feasibility is decided before any ranking."""
    reasons: list[CompositionReason] = []
    topology_places = {place.id for place in value.topology.places}
    for place in value.service_timing.places:
        if place.id not in topology_places:
            reasons.append(CompositionReason(code=CompositionReasonCode.TIMING_PLACE_NOT_IN_TOPOLOGY, reference_id=place.id))

    evidence_by_id = {fact.id: fact for fact in value.evidence}
    for identifier in value.required_evidence_ids:
        evidence = evidence_by_id.get(identifier)
        if evidence is None:
            reasons.append(CompositionReason(code=CompositionReasonCode.REQUIRED_EVIDENCE_MISSING, reference_id=identifier))
        elif evidence.coverage not in {CoverageState.SUPPORTED, CoverageState.MANUAL} or isinstance(evidence.value, UnknownEvidenceValue):
            reasons.append(CompositionReason(code=CompositionReasonCode.REQUIRED_EVIDENCE_UNKNOWN, reference_id=identifier))

    money = ComposedMoney(
        sunk_cost=_sum_money(tuple(item for item in value.money if item.timing is MoneyTiming.SUNK_COST)),
        cash_due_now=_sum_money(tuple(item for item in value.money if item.timing is MoneyTiming.CASH_REQUIRED_NOW)),
        unreceived_refund=_sum_money(tuple(item for item in value.money if item.timing is MoneyTiming.UNRECEIVED_REFUND)),
    )
    for summary in (money.sunk_cost, money.cash_due_now, money.unreceived_refund):
        if isinstance(summary, UnknownMoneyAmount):
            reasons.append(CompositionReason(code=CompositionReasonCode.MONEY_AMOUNT_UNKNOWN, reference_id="money:unknown"))
        elif isinstance(summary, RangeMoneyAmount):
            reasons.append(CompositionReason(code=CompositionReasonCode.MONEY_AMOUNT_RANGE, reference_id="money:range"))

    goals = evaluate_structurally(value.goal_evaluation)
    evidence_references = tuple(EvidenceReference(fact_id=fact.id, provenance_id=fact.provenance_id, coverage=fact.coverage) for fact in value.evidence)
    if any(reason.code is CompositionReasonCode.TIMING_PLACE_NOT_IN_TOPOLOGY for reason in reasons):
        outcome = ComposedOutcome.STRUCTURAL_ERROR
    elif goals.outcome is StructuralOutcome.KNOWN_INFEASIBLE:
        outcome = ComposedOutcome.KNOWN_INFEASIBLE
    elif goals.outcome is StructuralOutcome.MISSING_FACTS or any(reason.code in {CompositionReasonCode.REQUIRED_EVIDENCE_MISSING, CompositionReasonCode.REQUIRED_EVIDENCE_UNKNOWN} for reason in reasons):
        outcome = ComposedOutcome.MISSING_REQUIRED_FACTS
    elif reasons:
        outcome = ComposedOutcome.CONDITIONAL
    else:
        outcome = ComposedOutcome.FEASIBLE
    return GenericCompositionResult(outcome=outcome, reasons=tuple(reasons), goal_evaluation=goals, evidence_references=evidence_references, money=money)
