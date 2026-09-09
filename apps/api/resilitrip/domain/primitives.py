"""Evidence-aware, provider-independent facts and money primitives for real trips.

These models deliberately do not participate in the synthetic Mumbai--Goa fixture
or its planner.  Later real-trip slices can compose them without reinterpreting
the demo's accepted money values.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Annotated, Literal

from pydantic import Field, StringConstraints, model_validator
from typing_extensions import TypeAliasType

from resilitrip.domain.models import (
    ContractModel,
    DisplayLabel,
    EntityId,
    EvidenceValue,
    MoneyPaise,
    UnknownEvidenceValue,
)


class CoverageState(StrEnum):
    """What the selected source can currently say about a fact."""

    SUPPORTED = "supported"
    NOT_COVERED = "not_covered"
    TEMPORARILY_UNAVAILABLE = "temporarily_unavailable"
    UNKNOWN = "unknown"
    MANUAL = "manual"


class EvidenceFact(ContractModel):
    """One observed fact, including freshness and an explicit unknown variant."""

    id: EntityId
    provenance_id: EntityId
    observed_at: datetime
    fresh_until: datetime | None = None
    coverage: CoverageState
    value: EvidenceValue

    @model_validator(mode="after")
    def freshness_and_coverage_are_honest(self) -> "EvidenceFact":
        if self.fresh_until is not None and self.fresh_until < self.observed_at:
            raise ValueError("fresh_until must not precede observed_at")
        if self.coverage in {
            CoverageState.NOT_COVERED,
            CoverageState.TEMPORARILY_UNAVAILABLE,
            CoverageState.UNKNOWN,
        } and not isinstance(self.value, UnknownEvidenceValue):
            raise ValueError("unavailable coverage must use an explicit unknown value")
        return self


class ExactMoneyAmount(ContractModel):
    amount_kind: Literal["exact"]
    paise: MoneyPaise


class RangeMoneyAmount(ContractModel):
    amount_kind: Literal["range"]
    minimum_paise: MoneyPaise
    maximum_paise: MoneyPaise

    @model_validator(mode="after")
    def valid_range(self) -> "RangeMoneyAmount":
        if self.minimum_paise > self.maximum_paise:
            raise ValueError("minimum_paise must not exceed maximum_paise")
        return self


class UnknownMoneyAmount(ContractModel):
    amount_kind: Literal["unknown"]


MoneyAmount = TypeAliasType(
    "MoneyAmount",
    Annotated[
        ExactMoneyAmount | RangeMoneyAmount | UnknownMoneyAmount,
        Field(discriminator="amount_kind"),
    ],
)


class MoneyScope(StrEnum):
    PER_TRAVELER = "per_traveler"
    PARTY_TOTAL = "party_total"
    TRIP_TOTAL = "trip_total"
    ITEM_TOTAL = "item_total"


class MoneyTiming(StrEnum):
    SUNK_COST = "sunk_cost"
    CASH_REQUIRED_NOW = "cash_required_now"
    UNRECEIVED_REFUND = "unreceived_refund"


class MoneyFact(ContractModel):
    """A money statement without treating an unknown amount as zero."""

    id: EntityId
    amount: MoneyAmount
    party_id: EntityId
    party_label: DisplayLabel
    scope: MoneyScope
    timing: MoneyTiming
    description: Annotated[str, StringConstraints(min_length=1, max_length=200, strip_whitespace=True)]

