"""Pure Gate A2 plan finalization, finance, classification, frontier and ranking."""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta

from resilitrip.domain.evaluation import evaluate_itinerary
from resilitrip.domain.models import (
    AccessibilityState, ConstraintCheck, DomainReasonCode, EvidenceValue, FeasibilityStatus,
    MoneyCategory, MoneyItem, PaymentState, PlanEvaluation, PlanLifecycleStatus,
    PlanObjectiveValues, PlannerCounts, PlannerResult, PlannerResultStatus, RankingPreset,
    RankingReasonCode, SearchScope, ServiceStatus, TripAggregate, evidence_value,
)
from resilitrip.domain.recovery import AtomicCandidate, enumerate_atomic_candidates


def _evidence(kind: str, value, unit: str | None = None) -> EvidenceValue:
    return evidence_value(kind, value, unit)


def _constraint(identifier: str, passed: bool | None, reason: DomainReasonCode, observed, required, kind: str, unit: str | None = None, provenance: tuple[str, ...] = (), required_kind: str | None = None) -> ConstraintCheck:
    return ConstraintCheck(constraint_id=identifier, passed=passed, reason_code=reason,
        observed=_evidence(kind, observed, unit if kind != "unknown" else None),
        required=_evidence(required_kind or kind, required, unit), provenance_ids=provenance)


def replace_constraints(trip: TripAggregate, constraints) -> TripAggregate:
    """Return an isolated versioned constraint branch; persistence/API work remains out of scope."""
    return trip.model_copy(update={"version": trip.version + 1, "constraints": constraints,
        "last_mutation_kind": "constraints"})


def _plan_code(candidate: AtomicCandidate) -> str:
    return candidate.id.split(":")[1]


def build_money_items(candidate: AtomicCandidate, trip: TripAggregate, catalog) -> tuple[MoneyItem, ...]:
    code = _plan_code(candidate)
    if code == "WAIT-T1":
        wanted = {"money:C1-due", "money:C2-due"}
        return tuple(item for item in trip.baseline_money_items if item.id in wanted)
    services = {item.id: item for item in catalog.services}
    transfers = {item.id: item for item in catalog.transfer_templates}
    service_id = next(item for item in candidate.sequence if item.startswith("svc:F"))
    hotel_transfer_id = next(item for item in candidate.sequence if item.startswith("xfer:X-GO"))
    service, hotel_transfer = services[service_id], transfers[hotel_transfer_id]
    x1, c2 = transfers["xfer:X1"], transfers["xfer:C2"]
    values = (
        (f"money:{code}:X1", None, "xfer:X1", MoneyCategory.NEW_PURCHASE, x1.price_paise, x1.provenance_id),
        (f"money:{code}:fare", service_id, None, MoneyCategory.NEW_PURCHASE, service.price_paise, service.provenance_id),
        (f"money:{code}:{'GOX' if 'GOX' in hotel_transfer_id else 'GOI'}-hotel", None, hotel_transfer_id, MoneyCategory.NEW_PURCHASE, hotel_transfer.price_paise, hotel_transfer.provenance_id),
        (f"money:{code}:C2", None, "xfer:C2", MoneyCategory.RETAINED_CHARGE, c2.price_paise, c2.provenance_id),
    )
    return tuple(MoneyItem(id=identifier, booking_id="booking:cab-C2" if transfer_id == "xfer:C2" else None,
        service_id=service_id_value, transfer_template_id=transfer_id, category=category,
        payment_state=PaymentState.DUE, amount_paise=amount, provenance_id=provenance)
        for identifier, service_id_value, transfer_id, category, amount, provenance in values)


def _valid_until(candidate: AtomicCandidate, trip: TripAggregate, catalog) -> datetime:
    effective = {item.service_id: item for item in trip.effective_services}
    services = {item.id: item for item in catalog.services}
    transfers = {item.id: item for item in catalog.transfer_templates}
    cutoffs: list[datetime] = []
    for identifier in candidate.sequence:
        if identifier in services:
            cutoffs.append(effective[identifier].effective_departure - timedelta(seconds=services[identifier].origin_allowance_sec))
        elif identifier in transfers:
            cutoffs.append(transfers[identifier].latest_start)
    return min(cutoffs, default=trip.constraints.horizon_end)


def finalize_candidate(candidate: AtomicCandidate, trip: TripAggregate, catalog) -> PlanEvaluation:
    activities, timing_checks, timing_status = evaluate_itinerary(itinerary=candidate.itinerary, catalog=catalog,
        current_state=trip.current_state, effective_services=trip.effective_services,
        decision_allowance_sec=trip.decision_allowance_sec, risk_threshold_sec=trip.constraints.risk_threshold_sec,
        evaluation_mode="current")
    services = {item.id: item for item in catalog.services}
    transfers = {item.id: item for item in catalog.transfer_templates}
    effective = {item.service_id: item for item in trip.effective_services}
    checks = list(timing_checks)
    for identifier in candidate.sequence:
        if identifier in services:
            service = services[identifier]
            state = effective[identifier]
            capacity_passed = None if service.capacity is None else service.capacity >= trip.constraints.party_size
            reason = DomainReasonCode.CAPACITY_UNKNOWN if capacity_passed is None else DomainReasonCode.HARD_CONSTRAINTS_PASS if capacity_passed else DomainReasonCode.CAPACITY_INSUFFICIENT
            checks.append(_constraint(f"constraint:{identifier}:capacity", capacity_passed, reason, service.capacity,
                trip.constraints.party_size, "unknown" if service.capacity is None else "integer", provenance=(service.provenance_id,), required_kind="integer"))
            checks.append(_constraint(f"constraint:{identifier}:status", state.status is not ServiceStatus.CANCELLED,
                DomainReasonCode.SERVICE_CANCELLED if state.status is ServiceStatus.CANCELLED else DomainReasonCode.HARD_CONSTRAINTS_PASS,
                state.status.value, "not_cancelled", "text", provenance=(state.provenance_id,)))
            checks.append(_constraint(f"constraint:{identifier}:mode", service.mode.value in {mode.value for mode in trip.constraints.allowed_modes},
                DomainReasonCode.HARD_CONSTRAINTS_PASS if service.mode.value in {mode.value for mode in trip.constraints.allowed_modes} else DomainReasonCode.MODE_NOT_ALLOWED,
                service.mode.value, "allowed_modes", "text", provenance=(service.provenance_id,)))
        elif identifier in transfers:
            transfer = transfers[identifier]
            capacity_passed = None if transfer.capacity is None else transfer.capacity >= trip.constraints.party_size
            checks.append(_constraint(f"constraint:{identifier}:capacity", capacity_passed,
                DomainReasonCode.CAPACITY_UNKNOWN if capacity_passed is None else DomainReasonCode.HARD_CONSTRAINTS_PASS if capacity_passed else DomainReasonCode.CAPACITY_INSUFFICIENT,
                transfer.capacity, trip.constraints.party_size, "unknown" if transfer.capacity is None else "integer", provenance=(transfer.provenance_id,), required_kind="integer"))
            if trip.constraints.accessibility_required:
                accessibility_passed = None if transfer.accessibility is AccessibilityState.UNKNOWN else transfer.accessibility is AccessibilityState.SUITABLE
                checks.append(_constraint(f"constraint:{identifier}:accessibility", accessibility_passed,
                    DomainReasonCode.ACCESSIBILITY_UNKNOWN if accessibility_passed is None else DomainReasonCode.HARD_CONSTRAINTS_PASS if accessibility_passed else DomainReasonCode.ACCESSIBILITY_UNSUITABLE,
                    transfer.accessibility.value, "suitable", "text", provenance=(transfer.provenance_id,)))
    money_items = build_money_items(candidate, trip, catalog)
    commitment = next(item for item in activities if item.activity_id == "act:E1")
    cash = sum(item.amount_paise or 0 for item in money_items if item.payment_state is PaymentState.DUE)
    incremental = cash - trip.baseline_remaining_spend_paise
    cash_passed = cash <= trip.constraints.max_cash_required_paise
    incremental_passed = incremental <= trip.constraints.max_incremental_cost_paise
    checks.extend((
        _constraint("constraint:budget:cash_required", cash_passed, DomainReasonCode.HARD_CONSTRAINTS_PASS if cash_passed else DomainReasonCode.CASH_LIMIT_EXCEEDED,
            cash, trip.constraints.max_cash_required_paise, "money_paise", "INR_paise"),
        _constraint("constraint:budget:incremental_cost", incremental_passed, DomainReasonCode.HARD_CONSTRAINTS_PASS if incremental_passed else DomainReasonCode.EXTRA_COST_LIMIT_EXCEEDED,
            incremental, trip.constraints.max_incremental_cost_paise, "money_paise", "INR_paise"),
    ))
    new_services = sum(identifier.startswith("svc:F") for identifier in candidate.sequence)
    transfer_count = sum(identifier.startswith("xfer:") for identifier in candidate.sequence)
    checks.extend((
        _constraint("constraint:bounds:horizon", commitment.ready_at <= trip.constraints.horizon_end,
            DomainReasonCode.HARD_CONSTRAINTS_PASS if commitment.ready_at <= trip.constraints.horizon_end else DomainReasonCode.SEARCH_HORIZON_EXCEEDED,
            commitment.ready_at, trip.constraints.horizon_end, "timestamp"),
        _constraint("constraint:bounds:fixed_legs", new_services <= trip.constraints.max_new_fixed_legs,
            DomainReasonCode.HARD_CONSTRAINTS_PASS if new_services <= trip.constraints.max_new_fixed_legs else DomainReasonCode.MAX_FIXED_LEGS_EXCEEDED,
            new_services, trip.constraints.max_new_fixed_legs, "integer"),
        _constraint("constraint:bounds:transfer_legs", transfer_count <= trip.constraints.max_transfer_legs,
            DomainReasonCode.HARD_CONSTRAINTS_PASS if transfer_count <= trip.constraints.max_transfer_legs else DomainReasonCode.MAX_TRANSFER_LEGS_EXCEEDED,
            transfer_count, trip.constraints.max_transfer_legs, "integer"),
    ))
    false_reasons = tuple(dict.fromkeys(check.reason_code for check in checks if check.passed is False and check.reason_code is not DomainReasonCode.HARD_CONSTRAINTS_PASS))
    unknown_reasons = tuple(dict.fromkeys(check.reason_code for check in checks if check.passed is None))
    status = FeasibilityStatus.INFEASIBLE if timing_status in (FeasibilityStatus.INFEASIBLE, FeasibilityStatus.BLOCKED) or false_reasons else FeasibilityStatus.UNKNOWN if unknown_reasons else timing_status
    reason_codes = tuple(dict.fromkeys((*false_reasons, *unknown_reasons)))
    changed = () if _plan_code(candidate) == "WAIT-T1" else ("booking:train-original", "booking:cab-C1")
    provenance = tuple(dict.fromkeys(provenance for item in activities for provenance in item.provenance_ids))
    return PlanEvaluation(id=candidate.id, trip_id=trip.id, trip_version=trip.version, catalog_version=trip.catalog_version,
        run_id=None, lifecycle_status=PlanLifecycleStatus.PREVIEW, evaluation_status=status,
        valid_until=_valid_until(candidate, trip, catalog), sequence_ids=candidate.sequence,
        sequence_signature=candidate.signature, proposed_itinerary=candidate.itinerary, activity_sequence=activities,
        service_ids=tuple(item for item in candidate.sequence if item in services),
        transfer_template_ids=tuple(item for item in candidate.sequence if item in transfers), money_items=money_items,
        cash_required_paise=cash, incremental_cost_paise=incremental, potential_refund_paise=None,
        final_required_arrival_at=commitment.ready_at, event_slack_sec=commitment.slack_sec,
        changed_original_booking_ids=changed, constraint_checks=tuple(checks), provenance_ids=provenance,
        objective_values=PlanObjectiveValues(cash_required_paise=cash, final_required_arrival_at=commitment.ready_at,
            changed_original_booking_count=len(changed)), frontier_member=False, display_rank=None,
        ranking_reason_code=None, simulated=True, bookable=False, reason_codes=reason_codes)


def pareto_frontier(plans: tuple[PlanEvaluation, ...]) -> tuple[PlanEvaluation, ...]:
    def dominates(left: PlanEvaluation, right: PlanEvaluation) -> bool:
        a = (left.cash_required_paise, left.final_required_arrival_at, len(left.changed_original_booking_ids))
        b = (right.cash_required_paise, right.final_required_arrival_at, len(right.changed_original_booking_ids))
        return all(x <= y for x, y in zip(a, b)) and any(x < y for x, y in zip(a, b))
    return tuple(plan for plan in sorted(plans, key=lambda item: item.id) if not any(other.id != plan.id and dominates(other, plan) for other in plans))


def _rank(plans: tuple[PlanEvaluation, ...], preset: RankingPreset) -> tuple[PlanEvaluation, ...]:
    keys = {
        RankingPreset.CHEAPEST: lambda item: (item.cash_required_paise, item.final_required_arrival_at, len(item.changed_original_booking_ids), item.id),
        RankingPreset.FASTEST: lambda item: (item.final_required_arrival_at, item.cash_required_paise, len(item.changed_original_booking_ids), item.id),
        RankingPreset.FEWEST_CHANGES: lambda item: (len(item.changed_original_booking_ids), item.cash_required_paise, item.final_required_arrival_at, item.id),
    }
    reason = {RankingPreset.CHEAPEST: RankingReasonCode.LOWEST_CASH_ON_FRONTIER,
        RankingPreset.FASTEST: RankingReasonCode.EARLIEST_ARRIVAL_ON_FRONTIER,
        RankingPreset.FEWEST_CHANGES: RankingReasonCode.FEWEST_CHANGES_ON_FRONTIER}[preset]
    return tuple(plan.model_copy(update={"frontier_member": True, "display_rank": index,
        "ranking_reason_code": reason}) for index, plan in enumerate(sorted(plans, key=keys[preset]), 1))


def plan_recovery(trip: TripAggregate, catalog, *, ranking_preset: RankingPreset | None = None,
                  interrupt_before_search: bool = False) -> PlannerResult:
    preset = ranking_preset or trip.constraints.ranking_preset
    scope = SearchScope(catalog_version=trip.catalog_version, replay_as_of=trip.current_state.as_of,
        horizon_end=trip.constraints.horizon_end, max_catalog_services=len(catalog.services),
        max_new_fixed_legs=trip.constraints.max_new_fixed_legs, max_transfer_legs=trip.constraints.max_transfer_legs,
        max_activities=20)
    base = dict(run_id=f"run:{trip.id.split(':', 1)[-1]}:v{trip.version}:{preset.value}", trip_id=trip.id,
        trip_version=trip.version, catalog_version=trip.catalog_version, ranking_preset=preset, scope=scope, runtime_ms=0.0)
    if interrupt_before_search:
        counts = PlannerCounts(states_expanded=0, complete_paths=0, duplicate_paths=0, feasible_total=0,
            uncertain_total=0, rejected_total=0, frontier_total=0, displayed_total=0, pruned_by_reason={DomainReasonCode.SEARCH_INCOMPLETE: 1})
        return PlannerResult(**base, result_status=PlannerResultStatus.PARTIAL_SEARCH, search_complete=False,
            interruption_reason=DomainReasonCode.SEARCH_INCOMPLETE, counts=counts,
            feasible_plans=(), uncertain_plans=(), rejected_plans=())
    try:
        atomic = enumerate_atomic_candidates(trip, catalog)
    except ValueError as error:
        if str(error) != "UNSUPPORTED_CURRENT_STATE":
            raise
        counts = PlannerCounts(states_expanded=0, complete_paths=0, duplicate_paths=0, feasible_total=0,
            uncertain_total=0, rejected_total=0, frontier_total=0, displayed_total=0,
            pruned_by_reason={DomainReasonCode.UNSUPPORTED_CURRENT_STATE: 1})
        return PlannerResult(**base, result_status=PlannerResultStatus.NEEDS_INPUT, search_complete=False,
            interruption_reason=DomainReasonCode.UNSUPPORTED_CURRENT_STATE, counts=counts,
            feasible_plans=(), uncertain_plans=(), rejected_plans=())
    effective = {item.service_id: item for item in trip.effective_services}
    cancelled = tuple(candidate for candidate in atomic if any(
        identifier in effective and effective[identifier].status is ServiceStatus.CANCELLED
        for identifier in candidate.sequence
    ))
    finalizable = tuple(candidate for candidate in atomic if candidate not in cancelled)
    plans = tuple(finalize_candidate(candidate, trip, catalog) for candidate in finalizable)
    feasible = tuple(plan for plan in plans if plan.evaluation_status in (FeasibilityStatus.FEASIBLE, FeasibilityStatus.AT_RISK))
    uncertain = tuple(plan for plan in plans if plan.evaluation_status is FeasibilityStatus.UNKNOWN)
    rejected = tuple(plan for plan in plans if plan.evaluation_status in (FeasibilityStatus.INFEASIBLE, FeasibilityStatus.BLOCKED))
    ranked = _rank(pareto_frontier(feasible), preset)[:3]
    result_status = PlannerResultStatus.NEEDS_INPUT if uncertain and not feasible else PlannerResultStatus.COMPLETE if feasible else PlannerResultStatus.NO_FEASIBLE_CATALOG_PLAN
    pruned = {DomainReasonCode.SERVICE_CANCELLED: len(cancelled)} if cancelled else {}
    counts = PlannerCounts(states_expanded=len(atomic), complete_paths=len(finalizable), duplicate_paths=0,
        feasible_total=len(feasible), uncertain_total=len(uncertain), rejected_total=len(rejected),
        frontier_total=len(pareto_frontier(feasible)), displayed_total=len(ranked), pruned_by_reason=pruned)
    return PlannerResult(**base, result_status=result_status, search_complete=True, interruption_reason=None,
        counts=counts, feasible_plans=ranked, uncertain_plans=uncertain[:10], rejected_plans=rejected[:10])


def plan_adoptability(plan: PlanEvaluation, replay_as_of: datetime, *, search_complete: bool) -> tuple[bool, DomainReasonCode | None]:
    if not search_complete or plan.evaluation_status not in (FeasibilityStatus.FEASIBLE, FeasibilityStatus.AT_RISK):
        return False, DomainReasonCode.SEARCH_INCOMPLETE if not search_complete else plan.reason_codes[0]
    if replay_as_of >= plan.valid_until:
        return False, DomainReasonCode.STALE_PLAN
    return True, None
