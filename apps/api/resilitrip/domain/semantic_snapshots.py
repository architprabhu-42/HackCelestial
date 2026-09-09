"""Immutable, semantic alternative-plan evaluation snapshots for generic R1 work."""

from __future__ import annotations

import hashlib
import json
from datetime import datetime

from pydantic import Field, model_validator

from resilitrip.domain.composed_evaluation import (
    ComposedOutcome,
    GenericCompositionInput,
    GenericCompositionResult,
    compose_evaluation,
)
from resilitrip.domain.models import ContractModel, EntityId


class SemanticAlternativePlan(ContractModel):
    """Stable semantic identity and its revision; intentionally no rank or score."""

    semantic_id: EntityId
    revision: int = Field(strict=True, ge=1)
    topology_id: EntityId
    timing_id: EntityId
    goal_ids: tuple[EntityId, ...]
    evidence_ids: tuple[EntityId, ...]
    evaluation_status: ComposedOutcome


def _snapshot_content_hash(
    snapshot_id: str, trip_id: str, trip_version: int, created_at: datetime,
    evaluation_input: GenericCompositionInput, composed_evaluation: GenericCompositionResult,
    alternatives: tuple[SemanticAlternativePlan, ...],
) -> str:
    payload = {
        "id": snapshot_id, "trip_id": trip_id, "trip_version": trip_version,
        "created_at": created_at.isoformat(),
        "evaluation_input": evaluation_input.model_dump(mode="json"),
        "composed_evaluation": composed_evaluation.model_dump(mode="json"),
        "alternatives": [item.model_dump(mode="json") for item in alternatives],
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


class ImmutableEvaluationSnapshot(ContractModel):
    id: EntityId
    trip_id: EntityId
    trip_version: int = Field(strict=True, ge=1)
    created_at: datetime
    evaluation_input: GenericCompositionInput
    composed_evaluation: GenericCompositionResult
    alternatives: tuple[SemanticAlternativePlan, ...]
    content_hash: str

    @model_validator(mode="after")
    def references_and_immutable_content_are_valid(self) -> "ImmutableEvaluationSnapshot":
        semantic_ids = [alternative.semantic_id for alternative in self.alternatives]
        if len(semantic_ids) != len(set(semantic_ids)):
            raise ValueError("snapshot alternative semantic IDs must be unique")
        topology_id = self.evaluation_input.topology.id
        timing_id = self.evaluation_input.service_timing.id
        goal_ids = tuple(goal.id for goal in self.evaluation_input.goal_evaluation.goals)
        evidence_ids = tuple(fact.id for fact in self.evaluation_input.evidence)
        for alternative in self.alternatives:
            if alternative.topology_id != topology_id or alternative.timing_id != timing_id:
                raise ValueError("alternative topology/timing reference does not resolve")
            if alternative.goal_ids != goal_ids or alternative.evidence_ids != evidence_ids:
                raise ValueError("alternative goal/evidence reference does not resolve")
            if alternative.evaluation_status is not self.composed_evaluation.outcome:
                raise ValueError("alternative evaluation status must match snapshot result")
        if self.composed_evaluation != compose_evaluation(self.evaluation_input):
            raise ValueError("snapshot composed evaluation does not match its input")
        expected = _snapshot_content_hash(self.id, self.trip_id, self.trip_version, self.created_at, self.evaluation_input, self.composed_evaluation, self.alternatives)
        if self.content_hash != expected:
            raise ValueError("snapshot content hash does not match immutable content")
        return self


def create_evaluation_snapshot(
    *, snapshot_id: str, trip_id: str, trip_version: int, created_at: datetime,
    evaluation_input: GenericCompositionInput, alternatives: tuple[SemanticAlternativePlan, ...],
) -> ImmutableEvaluationSnapshot:
    """Create a content-hashed snapshot from a deterministic composed evaluation."""
    result = compose_evaluation(evaluation_input)
    digest = _snapshot_content_hash(snapshot_id, trip_id, trip_version, created_at, evaluation_input, result, alternatives)
    return ImmutableEvaluationSnapshot(
        id=snapshot_id, trip_id=trip_id, trip_version=trip_version, created_at=created_at,
        evaluation_input=evaluation_input, composed_evaluation=result, alternatives=alternatives,
        content_hash=digest,
    )


class EvaluationSnapshotHistory(ContractModel):
    """An append-only in-memory history; prior frozen snapshots are never rewritten."""

    snapshots: tuple[ImmutableEvaluationSnapshot, ...] = ()

    @model_validator(mode="after")
    def snapshots_are_append_only_and_revisions_progress(self) -> "EvaluationSnapshotHistory":
        snapshot_ids = [snapshot.id for snapshot in self.snapshots]
        if len(snapshot_ids) != len(set(snapshot_ids)):
            raise ValueError("snapshot IDs must be unique")
        latest_revision: dict[str, int] = {}
        latest_created_at: dict[str, datetime] = {}
        for snapshot in self.snapshots:
            # Revalidation detects model_copy attempts with stale hashes.
            ImmutableEvaluationSnapshot.model_validate(snapshot.model_dump(mode="python"))
            for alternative in snapshot.alternatives:
                previous = latest_revision.get(alternative.semantic_id, 0)
                if alternative.revision != previous + 1:
                    raise ValueError("alternative revisions must progress monotonically")
                previous_created = latest_created_at.get(alternative.semantic_id)
                if previous_created is not None and snapshot.created_at < previous_created:
                    raise ValueError("alternative snapshots must be ordered by creation time")
                latest_revision[alternative.semantic_id] = alternative.revision
                latest_created_at[alternative.semantic_id] = snapshot.created_at
        return self


def append_snapshot(history: EvaluationSnapshotHistory, snapshot: ImmutableEvaluationSnapshot) -> EvaluationSnapshotHistory:
    """Return a new frozen history, preserving every prior immutable snapshot."""
    return EvaluationSnapshotHistory(snapshots=(*history.snapshots, snapshot))
