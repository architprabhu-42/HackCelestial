"""Isolated aggregate for persisted generic R1 trips.

This model intentionally does not extend the Mumbai--Goa ``TripAggregate``.
It is the persistence boundary for the additive R1 domain slices only.
"""

from __future__ import annotations

from pydantic import Field, field_validator, model_validator

from resilitrip.domain.composed_evaluation import GenericCompositionInput
from resilitrip.domain.models import ContractModel, EntityId, TRUTH_LABEL, TripLifecycle, TripMode
from resilitrip.domain.semantic_snapshots import EvaluationSnapshotHistory


class GenericTripAggregate(ContractModel):
    """A versioned generic trip and its immutable semantic evaluation history."""

    id: EntityId
    version: int = Field(strict=True, ge=1)
    mode: TripMode
    lifecycle: TripLifecycle
    scenario_id: EntityId | None = None
    truth_label: str
    evaluation_input: GenericCompositionInput
    semantic_snapshots: EvaluationSnapshotHistory = EvaluationSnapshotHistory()

    @field_validator("truth_label")
    @classmethod
    def truth_label_is_present(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("truth_label must not be blank")
        return value

    @model_validator(mode="after")
    def mode_and_snapshot_boundaries_are_valid(self) -> "GenericTripAggregate":
        if self.mode is TripMode.REAL:
            if self.scenario_id is not None:
                raise ValueError("generic real trips must not carry a scenario identity")
            if self.truth_label == TRUTH_LABEL:
                raise ValueError("generic real trips must not carry the synthetic demo truth label")
        else:
            if self.scenario_id is None:
                raise ValueError("generic demo trips require a scenario identity")
            if self.truth_label != TRUTH_LABEL:
                raise ValueError("generic demo trips must retain the synthetic demo truth label")
            if self.lifecycle is not TripLifecycle.ACTIVE:
                raise ValueError("generic demo trips must remain active")

        for snapshot in self.semantic_snapshots.snapshots:
            if snapshot.trip_id != self.id:
                raise ValueError("semantic snapshot trip reference does not resolve")
            if snapshot.trip_version > self.version:
                raise ValueError("semantic snapshot cannot reference a future trip version")
        return self
