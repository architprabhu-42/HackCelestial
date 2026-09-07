"""Gate A3 transactional API routes."""
from __future__ import annotations
from contextlib import contextmanager
from uuid import uuid4
from fastapi import APIRouter, Body, Request
from resilitrip.api.contracts import *
from resilitrip.api.errors import ApiProblem
from resilitrip.application.snapshots import create_initial_trip, snapshot_for_trip
from resilitrip.domain.editing import validate_itinerary_replacement
from resilitrip.domain.validation import DomainValidationError, validate_manual_trip
from resilitrip.domain.events import apply_cancellation_event, apply_timing_event, calculate_impacts
from resilitrip.domain.models import EffectiveServiceState, ServiceStatus, TripAggregate, TRUTH_LABEL, PlanLifecycleStatus
from resilitrip.domain.planner import plan_adoptability, plan_recovery
from resilitrip.infrastructure.fixture_loader import load_fixture
from resilitrip.infrastructure.repositories import AdoptionRepository, CatalogRepository, EventRepository, PlanRepository, TripRepository, canonical_json
from resilitrip.infrastructure.sqlite import connect

router=APIRouter(prefix="/v1",tags=["trips"])
PROBLEMS={code:{"model":ProblemResponse} for code in (400,404,409,413,415,422,500,503)}
def _root():
    from pathlib import Path
    return Path(__file__).resolve().parents[5]
@contextmanager
def _db(request, *, write: bool = False):
    connection = connect(request.app.state.settings.database_path)
    try:
        if write:
            # Serialize the version check and write so concurrent commands cannot
            # both pass against the same snapshot.
            connection.execute("BEGIN IMMEDIATE")
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
def _not_found(kind): raise ApiProblem(404,f"{kind}_NOT_FOUND",f"{kind.title()} was not found.")
def _version(trip,expected):
    if trip.version!=expected: raise ApiProblem(409,"VERSION_CONFLICT","The trip changed. Refresh and try again.",retryable=True,current_trip_version=trip.version,current_catalog_version=trip.catalog_version)
def _provenance(trip, record):
    existing=next((item for item in trip.provenance if item.id==record.id),None)
    if existing and existing!=record: raise ApiProblem(409,"PROVENANCE_ID_CONFLICT","The provenance ID already exists with different content.")
    return trip.provenance if existing else (*trip.provenance,record)
def _snapshot(connection,trip,impacts=()): return snapshot_for_trip(trip,CatalogRepository(connection).get(trip.catalog_version),impacts)
def _validate_trip(connection, trip, *, current_state=None, constraints=None, itinerary=None, provenance=None, error_code=None):
    try:
        validate_manual_trip(catalog=CatalogRepository(connection).get(trip.catalog_version),
            traveler=trip.traveler, current_state=current_state or trip.current_state,
            constraints=constraints or trip.constraints, itinerary=itinerary or trip.active_itinerary,
            bookings=trip.bookings, money_items=trip.baseline_money_items,
            provenance=provenance or trip.provenance,
            constraints_provenance_id=trip.constraints_provenance_id,
            booking_activity_ids=tuple(item.id for item in trip.original_itinerary.activities))
    except DomainValidationError as exc:
        code=error_code or exc.code
        raise ApiProblem(422, code, str(exc), field_errors=({"path":exc.path,"code":code,"message":str(exc),"rejected_value":None},))
def _mutation(kind,prior,trip,changed,snapshot,staled=0):
    return MutationResponse(mutation_kind=kind,changed=changed,prior_trip_version=prior,current_trip_version=trip.version,staled_plan_count=staled,snapshot=snapshot)

@router.get("/scenarios",operation_id="list_scenarios",response_model=list[ScenarioSummary],responses=PROBLEMS)
def list_scenarios():
    fixture=load_fixture(_root())
    return [ScenarioSummary(id=fixture.scenario.id,name=fixture.scenario.name,catalog_version=fixture.catalog.catalog_version,
        display_timezone=fixture.scenario.display_timezone,currency=fixture.scenario.currency,truth_label=fixture.scenario.truth_label,available=True)]

@router.post("/trips",operation_id="create_trip",status_code=201,response_model=TripCreatedResponse,responses=PROBLEMS)
def create_trip(request:Request,body:TripCreateRequest=Body(...)):
    with _db(request, write=True) as connection:
        if isinstance(body,FixtureTripCreate):
            try: fixture=load_fixture(_root(),body.scenario_id)
            except (KeyError,FileNotFoundError): _not_found("SCENARIO")
            trip=create_initial_trip(fixture,f"trip:{uuid4()}")
            if body.display_name is not None: trip=trip.model_copy(update={"traveler":trip.traveler.model_copy(update={"display_name":body.display_name})})
            catalog=fixture.catalog
        else:
            if body.catalog.scenario_id is not None: raise ApiProblem(422,"VALIDATION_ERROR","Manual catalogs require scenario_id null.")
            try:
                validate_manual_trip(catalog=body.catalog, traveler=body.traveler,
                    current_state=body.current_state, constraints=body.constraints,
                    itinerary=body.original_itinerary, bookings=body.bookings,
                    money_items=body.baseline_money_items, provenance=body.trip_provenance,
                    constraints_provenance_id=body.constraints_provenance_id)
            except DomainValidationError as exc:
                raise ApiProblem(422, exc.code, str(exc), field_errors=({"path":exc.path,"code":exc.code,"message":str(exc),"rejected_value":None},))
            effective=tuple(EffectiveServiceState(service_id=s.id,effective_departure=s.scheduled_departure,effective_arrival=s.scheduled_arrival,status=ServiceStatus.SCHEDULED,last_event_id=None,provenance_id=s.provenance_id) for s in body.catalog.services)
            baseline=sum(item.amount_paise or 0 for item in body.baseline_money_items if item.payment_state.value=="due")
            trip=TripAggregate(schema_version="resilitrip-api-1.0",id=f"trip:{uuid4()}",version=1,scenario_id=None,mode="demo",display_timezone="Asia/Kolkata",currency="INR",truth_label=TRUTH_LABEL,traveler=body.traveler,catalog_version=body.catalog.catalog_version,decision_allowance_sec=body.decision_allowance_sec,current_state=body.current_state,constraints=body.constraints,original_itinerary=body.original_itinerary,active_itinerary=body.original_itinerary,bookings=body.bookings,baseline_money_items=body.baseline_money_items,baseline_remaining_spend_paise=baseline,effective_services=effective,provenance=body.trip_provenance,constraints_provenance_id=body.constraints_provenance_id)
            catalog=body.catalog
        CatalogRepository(connection).seed(catalog); TripRepository(connection).create_initial(trip)
        snap=_snapshot(connection,trip)
        return TripCreatedResponse(trip_id=trip.id,trip_version=1,catalog_version=trip.catalog_version,snapshot=snap)

@router.get("/trips/{trip_id}",operation_id="get_trip",response_model=TripSnapshotResponse,responses=PROBLEMS)
def get_trip(request:Request,trip_id:str):
    with _db(request) as c:
        try: trip=TripRepository(c).get_current(trip_id)
        except KeyError: _not_found("TRIP")
        return TripSnapshotResponse(snapshot=_snapshot(c,trip))

@router.put("/trips/{trip_id}/constraints",operation_id="replace_constraints",response_model=MutationResponse,responses=PROBLEMS)
def replace_constraints_route(request:Request,trip_id:str,body:ConstraintsReplaceCommand):
    with _db(request, write=True) as c:
        repo=TripRepository(c)
        try: trip=repo.get_current(trip_id)
        except KeyError: _not_found("TRIP")
        _version(trip,body.expected_trip_version); provenance=_provenance(trip,body.provenance)
        unchanged=trip.constraints==body.constraints and provenance==trip.provenance
        if unchanged: return _mutation("constraints",trip.version,trip,False,_snapshot(c,trip))
        _validate_trip(c, trip, constraints=body.constraints, provenance=provenance)
        next_trip=trip.model_copy(update={"version":trip.version+1,"constraints":body.constraints,"provenance":provenance,"constraints_provenance_id":body.provenance.id,"last_mutation_kind":"constraints"})
        stale=repo.save_version(trip.version,next_trip)
        return _mutation("constraints",trip.version,next_trip,True,_snapshot(c,next_trip),stale)

@router.put("/trips/{trip_id}/current-state",operation_id="replace_current_state",response_model=MutationResponse,responses=PROBLEMS)
def replace_current_state_route(request:Request,trip_id:str,body:CurrentStateReplaceCommand):
    if body.current_state.provenance_id!=body.provenance.id: raise ApiProblem(422,"INVALID_CURRENT_STATE","Current-state provenance does not match.")
    with _db(request, write=True) as c:
        repo=TripRepository(c)
        try: trip=repo.get_current(trip_id)
        except KeyError: _not_found("TRIP")
        _version(trip,body.expected_trip_version); provenance=_provenance(trip,body.provenance)
        if trip.current_state==body.current_state and provenance==trip.provenance: return _mutation("current_state",trip.version,trip,False,_snapshot(c,trip))
        _validate_trip(c, trip, current_state=body.current_state, provenance=provenance)
        next_trip=trip.model_copy(update={"version":trip.version+1,"current_state":body.current_state,"provenance":provenance,"last_mutation_kind":"current_state"})
        stale=repo.save_version(trip.version,next_trip)
        return _mutation("current_state",trip.version,next_trip,True,_snapshot(c,next_trip),stale)

@router.put("/trips/{trip_id}/itinerary",operation_id="replace_active_itinerary",response_model=MutationResponse,responses=PROBLEMS)
def replace_itinerary(request:Request,trip_id:str,body:ItineraryEditCommand):
    with _db(request, write=True) as c:
        repo=TripRepository(c)
        try: trip=repo.get_current(trip_id)
        except KeyError: _not_found("TRIP")
        _version(trip,body.expected_trip_version)
        if trip.active_itinerary==body.active_itinerary and trip.constraints==body.constraints:
            return _mutation("itinerary_edit",trip.version,trip,False,_snapshot(c,trip))
        provenance=_provenance(trip,body.provenance)
        try:
            validate_itinerary_replacement(trip.active_itinerary,body.active_itinerary,trip.current_state,
                acknowledge_hard_removal=body.acknowledge_hard_changes,
                required_commitment_ids=body.constraints.required_commitment_ids)
        except DomainValidationError:
            raise ApiProblem(422,"ITINERARY_EDIT_INVALID","The edited itinerary dependency graph is invalid.")
        except ValueError as exc:
            code=str(exc)
            if code not in {"COMPLETED_ACTIVITY_IMMUTABLE","ACTIVE_ACTIVITY_IMMUTABLE","HARD_CHANGE_ACKNOWLEDGEMENT_REQUIRED"}:
                code="ITINERARY_EDIT_INVALID"
            raise ApiProblem(409 if code!="ITINERARY_EDIT_INVALID" else 422,code,"The remaining journey edit is not allowed.")
        _validate_trip(c, trip, itinerary=body.active_itinerary, constraints=body.constraints,
            provenance=provenance, error_code="ITINERARY_EDIT_INVALID")
        next_trip=trip.model_copy(update={"version":trip.version+1,"active_itinerary":body.active_itinerary,
            "constraints":body.constraints,"provenance":provenance,
            "constraints_provenance_id":body.provenance.id,"last_mutation_kind":"itinerary_edit"})
        stale=repo.save_version(trip.version,next_trip)
        return _mutation("itinerary_edit",trip.version,next_trip,True,_snapshot(c,next_trip),stale)

@router.post("/trips/{trip_id}/events",operation_id="apply_event",response_model=EventResponse,responses=PROBLEMS)
def apply_event_route(request:Request,trip_id:str,body:EventCommand):
    with _db(request, write=True) as c:
        trips=TripRepository(c); events=EventRepository(c)
        try: trip=trips.get_current(trip_id)
        except KeyError: _not_found("TRIP")
        prior=events.find(trip_id,body.event_id)
        if prior:
            if prior[0]!=canonical_json(body.model_dump(mode="json")): raise ApiProblem(409,"EVENT_ID_CONFLICT","The event ID already has different content.")
            return EventResponse(event_result=EventResult(disposition="duplicate",applied=False,event_id=body.event_id,prior_trip_version=prior[2]-1,current_trip_version=trip.version,snapshot=_snapshot(c,trip)))
        _version(trip,body.expected_trip_version)
        if body.provenance.observed_at != body.observed_at:
            raise ApiProblem(422, "VALIDATION_ERROR", "Event provenance observed_at must match the event.")
        _provenance(trip, body.provenance)
        latest_sequence = events.latest_sequence(trip_id, body.source_id)
        if latest_sequence is not None and body.source_sequence <= latest_sequence:
            raise ApiProblem(
                409,
                "EVENT_SEQUENCE_STALE",
                "The source sequence is not newer than the last applied event.",
                current_trip_version=trip.version,
            )
        try: next_trip=apply_timing_event(trip,body) if isinstance(body,TimingReplayEvent) else apply_cancellation_event(trip,body)
        except ValueError as exc: raise ApiProblem(409,str(exc),"The event conflicts with current state.",current_trip_version=trip.version)
        impacts=calculate_impacts(trip,next_trip,CatalogRepository(c).get(trip.catalog_version),body)
        events.add(trip_id,body,next_trip.version); trips.save_version(trip.version,next_trip)
        return EventResponse(event_result=EventResult(disposition="applied",applied=True,event_id=body.event_id,prior_trip_version=trip.version,current_trip_version=next_trip.version,snapshot=_snapshot(c,next_trip,impacts)))

@router.post("/trips/{trip_id}/plans",operation_id="generate_plans",response_model=PlannerResponse,responses=PROBLEMS)
def generate_plans(request:Request,trip_id:str,body:PlannerCommand):
    with _db(request, write=True) as c:
        trips=TripRepository(c)
        try: trip=trips.get_current(trip_id)
        except KeyError: _not_found("TRIP")
        _version(trip,body.expected_trip_version)
        if trip.catalog_version!=body.expected_catalog_version: raise ApiProblem(409,"CATALOG_VERSION_CONFLICT","The catalog changed.",retryable=True,current_catalog_version=trip.catalog_version)
        interrupt = request.app.state.settings.allow_test_controls and request.headers.get("X-ResiliTrip-Test-Control") == "partial_search"
        result=plan_recovery(trip,CatalogRepository(c).get(trip.catalog_version),ranking_preset=body.ranking_preset,
            interrupt_before_search=interrupt)
        current=trips.get_current(trip_id)
        if current.version!=trip.version: raise ApiProblem(409,"VERSION_CONFLICT","The trip changed during planning.",retryable=True,current_trip_version=current.version)
        run_id=f"run:{uuid4()}"
        result=result.model_copy(update={
            "run_id":run_id,
            "feasible_plans":tuple(p.model_copy(update={"run_id":run_id}) for p in result.feasible_plans),
            "uncertain_plans":tuple(p.model_copy(update={"run_id":run_id}) for p in result.uncertain_plans),
            "rejected_plans":tuple(p.model_copy(update={"run_id":run_id}) for p in result.rejected_plans),
        })
        PlanRepository(c).save_result(result)
        return PlannerResponse(planner_result=result,snapshot_version=trip.version,catalog_version=trip.catalog_version)

@router.get("/trips/{trip_id}/plans/{plan_id}",operation_id="get_plan",response_model=PlanEvaluation,responses=PROBLEMS)
def get_plan(request:Request,trip_id:str,plan_id:str):
    with _db(request) as c:
        try: plan,_,lifecycle=PlanRepository(c).get(trip_id,plan_id)
        except KeyError: _not_found("PLAN")
        return plan.model_copy(update={"run_id":None,"lifecycle_status":PlanLifecycleStatus(lifecycle)})

@router.post("/trips/{trip_id}/adoptions",operation_id="adopt_plan",response_model=AdoptionResponse,responses=PROBLEMS)
def adopt_plan(request:Request,trip_id:str,body:AdoptionCommand):
    with _db(request, write=True) as c:
        trips=TripRepository(c); plans=PlanRepository(c)
        try: trip=trips.get_current(trip_id)
        except KeyError: _not_found("TRIP")
        _version(trip,body.expected_trip_version)
        try: plan,complete,lifecycle=plans.get(trip_id,body.plan_id)
        except KeyError: _not_found("PLAN")
        if lifecycle!="preview" or plan.trip_version!=trip.version or plan.catalog_version!=trip.catalog_version: raise ApiProblem(409,"STALE_PLAN","The plan no longer matches the trip.",retryable=True,current_trip_version=trip.version,current_catalog_version=trip.catalog_version)
        allowed,reason=plan_adoptability(plan,trip.current_state.as_of,search_complete=complete)
        if not allowed: raise ApiProblem(409,"PLAN_EXPIRED" if reason and reason.value=="STALE_PLAN" else "PLAN_NOT_ADOPTABLE","The plan cannot be adopted.")
        fresh=plan_recovery(trip,CatalogRepository(c).get(trip.catalog_version),ranking_preset=trip.constraints.ranking_preset)
        match=next((p for p in (*fresh.feasible_plans,*fresh.uncertain_plans,*fresh.rejected_plans) if p.id==plan.id and p.sequence_signature==plan.sequence_signature),None)
        if not match: raise ApiProblem(409,"PLAN_NOT_ADOPTABLE","Plan revalidation failed.")
        next_trip=trip.model_copy(update={"version":trip.version+1,"active_itinerary":plan.proposed_itinerary,"adopted_plan_id":plan.id,"last_mutation_kind":"adoption"})
        trips.save_version(trip.version,next_trip); plans.set_adopted(trip_id,plan.id)
        record=AdoptionRecord(id=f"adoption:{uuid4()}",trip_id=trip.id,plan_id=plan.id,prior_trip_version=trip.version,resulting_trip_version=next_trip.version,catalog_version=trip.catalog_version,adopted_at=trip.current_state.as_of,acknowledge_simulation=True,external_booking_executed=False)
        AdoptionRepository(c).add(record)
        actions=(ProviderAction(id=f"provider-action:{plan.id.split(':')[1]}-availability",title="Verify the selected flight and fare",provider_key="airline_or_ota",status="not_started",required_before_external_change=True,reason="ResiliTrip used a synthetic option and did not reserve a seat.",handoff_available=True),)
        return AdoptionResponse(adoption=record,provider_actions=actions,snapshot=_snapshot(c,next_trip))

@router.post("/trips/{trip_id}/reset",operation_id="reset_trip",response_model=MutationResponse,responses=PROBLEMS)
def reset_trip(request:Request,trip_id:str,body:ResetCommand):
    with _db(request, write=True) as c:
        repo=TripRepository(c)
        try: trip=repo.get_current(trip_id)
        except KeyError: _not_found("TRIP")
        _version(trip,body.expected_trip_version)
        if trip.scenario_id is None or trip.scenario_id!=body.scenario_id: raise ApiProblem(409,"RESET_NOT_SUPPORTED","This trip cannot be reset.")
        fixture=load_fixture(_root(),body.scenario_id); restored=create_initial_trip(fixture,trip.id).model_copy(update={"version":trip.version+1,"last_mutation_kind":"reset"})
        stale=repo.save_version(trip.version,restored)
        return _mutation("reset",trip.version,restored,True,_snapshot(c,restored),stale)
