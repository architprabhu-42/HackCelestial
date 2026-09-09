"""Generic, provider-independent trip topology primitives.

This module intentionally has no relationship to the synthetic demo catalog,
planner, persistence, or API.  It describes structure only: no schedules, fares,
coordinates, availability, or generated alternatives are implied.
"""

from __future__ import annotations

from enum import StrEnum

from pydantic import model_validator

from resilitrip.domain.models import ContractModel, DisplayLabel, EntityId


class PlaceInputType(StrEnum):
    PROVIDER = "provider"
    MANUAL = "manual"
    UNKNOWN = "unknown"


class GenericTransportMode(StrEnum):
    RAIL = "rail"
    AIR = "air"
    BUS = "bus"
    LOCAL_TRANSIT = "local_transit"
    CAR = "car"
    WALK = "walk"
    MANUAL_FERRY = "manual_ferry"


class DependencyStrength(StrEnum):
    HARD = "hard"
    NON_HARD = "non_hard"


class DependencyType(StrEnum):
    SEQUENCE = "sequence"
    CONSTRAINT = "constraint"
    PREFERENCE = "preference"


class GenericPlace(ContractModel):
    """A route node whose origin remains explicit when facts are unavailable."""

    id: EntityId
    label: DisplayLabel
    input_type: PlaceInputType
    provider_reference: str | None = None

    @model_validator(mode="after")
    def explicit_origin(self) -> "GenericPlace":
        if self.input_type is PlaceInputType.PROVIDER and not self.provider_reference:
            raise ValueError("provider places require provider_reference")
        if self.input_type is not PlaceInputType.PROVIDER and self.provider_reference is not None:
            raise ValueError("manual or unknown places must not claim a provider reference")
        return self


class PhysicalRouteSegment(ContractModel):
    """One ordered physical movement, without asserting a service or timetable."""

    id: EntityId
    origin_place_id: EntityId
    destination_place_id: EntityId
    mode: GenericTransportMode

    @model_validator(mode="after")
    def movement_has_distinct_endpoints(self) -> "PhysicalRouteSegment":
        if self.origin_place_id == self.destination_place_id:
            raise ValueError("route segment endpoints must differ")
        return self


class SemanticTripItem(ContractModel):
    """A semantic trip concern, deliberately separate from physical movement."""

    id: EntityId
    label: DisplayLabel


class SemanticDependency(ContractModel):
    id: EntityId
    predecessor_item_id: EntityId
    successor_item_id: EntityId
    strength: DependencyStrength
    dependency_type: DependencyType

    @model_validator(mode="after")
    def links_distinct_items(self) -> "SemanticDependency":
        if self.predecessor_item_id == self.successor_item_id:
            raise ValueError("a semantic dependency cannot reference the same item")
        return self


class AlternativePlanReference(ContractModel):
    """Stable identity only; no ranking, search result, or generated plan data."""

    id: EntityId
    topology_id: EntityId
    label: DisplayLabel


class GenericTripTopology(ContractModel):
    """An ordered physical route plus a separate, acyclic semantic dependency DAG."""

    id: EntityId
    places: tuple[GenericPlace, ...]
    route_segments: tuple[PhysicalRouteSegment, ...]
    semantic_items: tuple[SemanticTripItem, ...]
    semantic_dependencies: tuple[SemanticDependency, ...]
    alternative_plan_references: tuple[AlternativePlanReference, ...] = ()

    @model_validator(mode="after")
    def valid_topology(self) -> "GenericTripTopology":
        collections = (
            self.places,
            self.route_segments,
            self.semantic_items,
            self.semantic_dependencies,
            self.alternative_plan_references,
        )
        identifiers = [self.id, *(entry.id for collection in collections for entry in collection)]
        if len(identifiers) != len(set(identifiers)):
            raise ValueError("topology identifiers must be unique")

        place_ids = {place.id for place in self.places}
        for segment in self.route_segments:
            if segment.origin_place_id not in place_ids or segment.destination_place_id not in place_ids:
                raise ValueError("route segment place reference does not resolve")
        for previous, following in zip(self.route_segments, self.route_segments[1:]):
            if previous.destination_place_id != following.origin_place_id:
                raise ValueError("route segments must be contiguous in declared order")

        item_ids = {item.id for item in self.semantic_items}
        adjacency = {item_id: set() for item_id in item_ids}
        for dependency in self.semantic_dependencies:
            if dependency.predecessor_item_id not in item_ids or dependency.successor_item_id not in item_ids:
                raise ValueError("semantic dependency item reference does not resolve")
            adjacency[dependency.predecessor_item_id].add(dependency.successor_item_id)
        visiting: set[str] = set()
        visited: set[str] = set()

        def visit(item_id: str) -> None:
            if item_id in visiting:
                raise ValueError("semantic dependencies must be acyclic")
            if item_id in visited:
                return
            visiting.add(item_id)
            for successor_id in adjacency[item_id]:
                visit(successor_id)
            visiting.remove(item_id)
            visited.add(item_id)

        for item_id in adjacency:
            visit(item_id)
        if any(reference.topology_id != self.id for reference in self.alternative_plan_references):
            raise ValueError("alternative plan references must identify this topology")
        return self
