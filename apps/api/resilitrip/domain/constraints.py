"""Exact, side-effect-free A1 constraint boundary rules."""

from __future__ import annotations

from datetime import datetime, timedelta

from resilitrip.domain.models import FeasibilityStatus, TransferTemplate


def classify_slack(slack_sec: int, risk_threshold_sec: int) -> FeasibilityStatus:
    """Classify slack: zero remains feasible but at risk; threshold itself is safe."""
    if slack_sec < 0:
        return FeasibilityStatus.INFEASIBLE
    if slack_sec < risk_threshold_sec:
        return FeasibilityStatus.AT_RISK
    return FeasibilityStatus.FEASIBLE


def service_cutoff(departure_at: datetime, origin_allowance_sec: int) -> datetime:
    return departure_at - timedelta(seconds=origin_allowance_sec)


def meets_cutoff(arrival_at: datetime, cutoff_at: datetime) -> bool:
    """Arrival at the cutoff is valid; later arrival is not."""
    return arrival_at <= cutoff_at


def hotel_start_is_valid(start_at: datetime, latest_start: datetime) -> bool:
    return start_at <= latest_start


def money_within_limits(cash_required_paise: int, incremental_cost_paise: int, max_cash_paise: int, max_incremental_paise: int) -> bool:
    return cash_required_paise <= max_cash_paise and incremental_cost_paise <= max_incremental_paise


def plan_is_valid(as_of: datetime, valid_until: datetime) -> bool:
    """Validity is exclusive at valid_until."""
    return as_of < valid_until


def schedule_flexible_transfer(ready_at: datetime, transfer: TransferTemplate) -> tuple[datetime, datetime]:
    start_at = max(ready_at, transfer.window_start)
    if start_at > transfer.latest_start:
        raise ValueError("ACTIVITY_WINDOW_MISSED")
    return start_at, start_at + timedelta(seconds=transfer.duration_sec)


def require_location_continuity(previous_location_id: str, next_origin_id: str) -> None:
    if previous_location_id != next_origin_id:
        raise ValueError("LOCATION_UNREACHABLE")


def validate_onboard_state(active_service_id: str | None, next_recovery_point_id: str | None, service_destination_id: str | None) -> str:
    """Return the only allowed recovery point; never infer a location such as CSMT."""
    if not active_service_id or not next_recovery_point_id or next_recovery_point_id != service_destination_id:
        raise ValueError("UNSUPPORTED_CURRENT_STATE")
    return next_recovery_point_id
