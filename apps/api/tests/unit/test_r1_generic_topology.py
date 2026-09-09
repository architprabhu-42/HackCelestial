import pytest
from pydantic import ValidationError

from resilitrip.application.snapshots import create_initial_trip
from resilitrip.domain.events import apply_timing_event
from resilitrip.domain.models import TRUTH_LABEL
from resilitrip.domain.planner import plan_recovery
from resilitrip.domain.topology import (
    AlternativePlanReference,
    DependencyStrength,
    DependencyType,
    GenericPlace,
    GenericTransportMode,
    GenericTripTopology,
    PhysicalRouteSegment,
    PlaceInputType,
    SemanticDependency,
    SemanticTripItem,
)


def topology(**updates) -> GenericTripTopology:
    values = {
        "id": "topology:weekend",
        "places": (
            GenericPlace(id="place:home", label="Home", input_type=PlaceInputType.MANUAL),
            GenericPlace(id="place:station", label="Station", input_type=PlaceInputType.PROVIDER, provider_reference="place:123"),
            GenericPlace(id="place:destination", label="Destination", input_type=PlaceInputType.UNKNOWN),
        ),
        "route_segments": (
            PhysicalRouteSegment(id="route:walk", origin_place_id="place:home", destination_place_id="place:station", mode=GenericTransportMode.WALK),
            PhysicalRouteSegment(id="route:rail", origin_place_id="place:station", destination_place_id="place:destination", mode=GenericTransportMode.RAIL),
        ),
        "semantic_items": (
            SemanticTripItem(id="item:leave", label="Leave home"),
            SemanticTripItem(id="item:arrive", label="Arrive"),
            SemanticTripItem(id="item:checkin", label="Check in"),
        ),
        "semantic_dependencies": (
            SemanticDependency(id="dependency:hard", predecessor_item_id="item:leave", successor_item_id="item:arrive", strength=DependencyStrength.HARD, dependency_type=DependencyType.SEQUENCE),
            SemanticDependency(id="dependency:soft", predecessor_item_id="item:arrive", successor_item_id="item:checkin", strength=DependencyStrength.NON_HARD, dependency_type=DependencyType.PREFERENCE),
        ),
        "alternative_plan_references": (AlternativePlanReference(id="alternative:one", topology_id="topology:weekend", label="Manual fallback"),),
    }
    values.update(updates)
    return GenericTripTopology(**values)


def test_r1_valid_multi_segment_route_and_separate_semantic_dag():
    value = topology()
    assert [segment.mode for segment in value.route_segments] == [GenericTransportMode.WALK, GenericTransportMode.RAIL]
    assert [dependency.strength for dependency in value.semantic_dependencies] == [DependencyStrength.HARD, DependencyStrength.NON_HARD]
    assert value.semantic_dependencies[0].dependency_type is DependencyType.SEQUENCE
    assert value.alternative_plan_references[0].id == "alternative:one"


def test_r1_manual_and_unknown_places_remain_explicit_without_provider_facts():
    value = topology()
    assert value.places[0].input_type is PlaceInputType.MANUAL
    assert value.places[0].provider_reference is None
    assert value.places[-1].input_type is PlaceInputType.UNKNOWN
    with pytest.raises(ValidationError, match="provider reference"):
        GenericPlace(id="place:invalid", label="Invented", input_type=PlaceInputType.UNKNOWN, provider_reference="provider:invented")


def test_r1_rejects_non_contiguous_or_dangling_route_references():
    broken = PhysicalRouteSegment(id="route:broken", origin_place_id="place:home", destination_place_id="place:destination", mode=GenericTransportMode.CAR)
    with pytest.raises(ValidationError, match="contiguous"):
        topology(route_segments=(topology().route_segments[0], broken))
    with pytest.raises(ValidationError, match="place reference"):
        topology(route_segments=(PhysicalRouteSegment(id="route:dangling", origin_place_id="place:missing", destination_place_id="place:station", mode=GenericTransportMode.BUS),))


def test_r1_rejects_dangling_dependency_and_cycles():
    with pytest.raises(ValidationError, match="item reference"):
        topology(semantic_dependencies=(SemanticDependency(id="dependency:dangling", predecessor_item_id="item:leave", successor_item_id="item:missing", strength=DependencyStrength.HARD, dependency_type=DependencyType.CONSTRAINT),))
    with pytest.raises(ValidationError, match="acyclic"):
        topology(semantic_dependencies=(
            SemanticDependency(id="dependency:one", predecessor_item_id="item:leave", successor_item_id="item:arrive", strength=DependencyStrength.HARD, dependency_type=DependencyType.SEQUENCE),
            SemanticDependency(id="dependency:two", predecessor_item_id="item:arrive", successor_item_id="item:leave", strength=DependencyStrength.HARD, dependency_type=DependencyType.SEQUENCE),
        ))


def test_r1_rejects_duplicate_topology_identifiers():
    with pytest.raises(ValidationError, match="identifiers must be unique"):
        topology(alternative_plan_references=(
            AlternativePlanReference(id="route:walk", topology_id="topology:weekend", label="Duplicate identity"),
        ))


def test_r1_topology_does_not_change_mumbai_goa_fixture_planner_or_truth_label(hero_fixture):
    trip = apply_timing_event(create_initial_trip(hero_fixture), hero_fixture.replay_events[0])
    plans = {plan.id.split(":")[1]: plan for plan in plan_recovery(trip, hero_fixture.catalog).feasible_plans}
    assert trip.truth_label == TRUTH_LABEL
    assert trip.mode.value == "demo" and trip.lifecycle.value == "active"
    assert {code: (plan.cash_required_paise, plan.incremental_cost_paise) for code, plan in plans.items()} == {
        "F2": (970_000, 840_000), "F3": (650_000, 520_000),
    }
