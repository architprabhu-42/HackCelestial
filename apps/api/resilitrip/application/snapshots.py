"""Gate A1 creation of a version-one trip and its baseline projection."""

from __future__ import annotations

from resilitrip.domain.baseline import evaluate_baseline
from resilitrip.domain.events import evaluate_trip
from resilitrip.domain.models import (
    EffectiveServiceState,
    ExecutableScenarioFixture,
    TripAggregate,
    TripViewSnapshot,
    ServiceStatus,
    ServiceCatalog,
    TRUTH_LABEL,
)


def create_initial_trip(fixture: ExecutableScenarioFixture, trip_id: str = "trip:mumbai-goa-v2") -> TripAggregate:
    effective_services = tuple(
        EffectiveServiceState(
            service_id=service.id,
            effective_departure=service.scheduled_departure,
            effective_arrival=service.scheduled_arrival,
            status=ServiceStatus.SCHEDULED,
            last_event_id=None,
            provenance_id=service.provenance_id,
        )
        for service in fixture.catalog.services
    )
    baseline_remaining = sum(
        item.amount_paise or 0 for item in fixture.baseline_money_items if item.payment_state.value == "due"
    )
    return TripAggregate(
        schema_version="resilitrip-api-1.0", id=trip_id, version=1,
        scenario_id=fixture.scenario.id, mode="demo", display_timezone="Asia/Kolkata", currency="INR",
        truth_label=TRUTH_LABEL, traveler=fixture.traveler,
        catalog_version=fixture.catalog.catalog_version, decision_allowance_sec=fixture.scenario.decision_allowance_sec,
        current_state=fixture.current_state, constraints=fixture.constraints,
        original_itinerary=fixture.original_itinerary, active_itinerary=fixture.original_itinerary,
        bookings=fixture.bookings, baseline_money_items=fixture.baseline_money_items,
        baseline_remaining_spend_paise=baseline_remaining, effective_services=effective_services,
        provenance=fixture.trip_provenance, constraints_provenance_id=fixture.constraints_provenance_id,
    )


def baseline_snapshot(fixture: ExecutableScenarioFixture, trip_id: str = "trip:mumbai-goa-v2") -> TripViewSnapshot:
    trip = create_initial_trip(fixture, trip_id)
    evaluated, overall = evaluate_baseline(fixture)
    provenance = tuple({item.id: item for item in (*fixture.catalog.provenance, *fixture.trip_provenance)}.values())
    return TripViewSnapshot(
        trip=trip, catalog=fixture.catalog, evaluated_itinerary=evaluated, overall_status=overall,
        provenance=provenance,
        available_actions={"can_apply_event": True, "can_edit_constraints": True, "can_edit_current_state": True,
                           "can_edit_itinerary": True, "can_generate_plans": True,
                           "can_adopt_plan": False, "can_reset": True},
    )


def snapshot_for_trip(trip: TripAggregate, catalog: ServiceCatalog, impacts=()) -> TripViewSnapshot:
    evaluated, _, overall = evaluate_trip(trip, catalog, evaluation_mode="current")
    provenance = tuple({item.id: item for item in (*catalog.provenance, *trip.provenance)}.values())
    return TripViewSnapshot(trip=trip, catalog=catalog, evaluated_itinerary=evaluated, overall_status=overall,
        impacts=tuple(impacts), provenance=provenance,
        available_actions={"can_apply_event": True, "can_edit_constraints": True,
            "can_edit_current_state": True, "can_edit_itinerary": True, "can_generate_plans": True,
            "can_adopt_plan": True, "can_reset": trip.scenario_id is not None})
