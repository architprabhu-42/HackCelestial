import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from fastapi.testclient import TestClient

from resilitrip.config import Settings
from resilitrip.infrastructure.fixture_loader import load_fixture
from resilitrip.infrastructure.sqlite import connect
from resilitrip.main import create_app
from resilitrip.infrastructure.repositories import AdoptionRepository, PlanRepository, TripRepository


def client_for(tmp_path):
    return TestClient(create_app(Settings(database_path=tmp_path / "a3.sqlite3")))


def apply_d1(client):
    fixture=load_fixture(Path(__file__).parents[4])
    return client.post("/api/v1/trips/trip:mumbai-goa-v2/events",json=fixture.replay_events[0].model_dump(mode="json"))


def generate(client,version=2):
    return client.post("/api/v1/trips/trip:mumbai-goa-v2/plans",json={"expected_trip_version":version,"expected_catalog_version":"catalog:mumbai-goa-v2","ranking_preset":"cheapest"})


def edit_command(snapshot, *, version, itinerary=None, constraints=None, acknowledge=False, suffix="edit"):
    fixture = load_fixture(Path(__file__).parents[4])
    provenance = fixture.trip_provenance[0].model_copy(update={
        "id": f"prov:user:{suffix}", "source_ref": f"user-action:{suffix}",
    })
    return {
        "expected_trip_version": version,
        "active_itinerary": itinerary or snapshot["trip"]["active_itinerary"],
        "constraints": constraints or snapshot["trip"]["constraints"],
        "acknowledge_hard_changes": acknowledge,
        "provenance": provenance.model_dump(mode="json"),
    }


def test_t13_t14_t15_real_api_adoption_and_truth_boundary(tmp_path):
    with client_for(tmp_path) as client:
        assert client.get("/api/v1/scenarios").status_code==200
        event=apply_d1(client); assert event.status_code==200 and event.json()["event_result"]["current_trip_version"]==2
        planned=generate(client); assert planned.status_code==200
        body=planned.json()["planner_result"]
        assert [item["id"] for item in body["feasible_plans"]]==["plan:F3:v2","plan:F2:v2"]
        looked=client.get("/api/v1/trips/trip:mumbai-goa-v2/plans/plan:F3:v2")
        assert looked.status_code==200 and looked.json()["simulated"] is True and looked.json()["bookable"] is False
        adopted=client.post("/api/v1/trips/trip:mumbai-goa-v2/adoptions",json={"expected_trip_version":2,"plan_id":"plan:F3:v2","acknowledge_simulation":True})
        assert adopted.status_code==200
        result=adopted.json()
        assert result["adoption"]["resulting_trip_version"]==3
        assert result["adoption"]["external_booking_executed"] is False
        assert {item["provider_key"] for item in result["provider_actions"]}<={"indian_rail_enquiry","airline_or_ota","hotel","local_transfer"}
        assert result["snapshot"]["trip"]["truth_label"]=="SYNTHETIC SCENARIO — NOT BOOKABLE"
        assert result["snapshot"]["trip"]["bookings"]==event.json()["event_result"]["snapshot"]["trip"]["bookings"]


def test_t16_t17_stale_no_plan_and_reset(tmp_path):
    with client_for(tmp_path) as client:
        apply_d1(client); generate(client)
        fixture=load_fixture(Path(__file__).parents[4])
        command={"expected_trip_version":2,"constraints":fixture.constraints.model_dump(mode="json"),"provenance":fixture.trip_provenance[0].model_copy(update={"id":"prov:user:new-constraints"}).model_dump(mode="json")}
        changed=client.put("/api/v1/trips/trip:mumbai-goa-v2/constraints",json=command)
        assert changed.status_code==200 and changed.json()["current_trip_version"]==3
        stale=client.post("/api/v1/trips/trip:mumbai-goa-v2/adoptions",json={"expected_trip_version":3,"plan_id":"plan:F3:v2","acknowledge_simulation":True})
        assert stale.status_code==409 and stale.json()["error"]["code"]=="STALE_PLAN"
        reset=client.post("/api/v1/trips/trip:mumbai-goa-v2/reset",json={"expected_trip_version":3,"scenario_id":"mumbai-goa-v2"})
        assert reset.status_code==200 and reset.json()["current_trip_version"]==4
        assert reset.json()["snapshot"]["trip"]["effective_services"][0]["effective_departure"]=="2026-09-26T06:00:00+05:30"


def test_t19_duplicate_conflict_and_stale_events_are_atomic(tmp_path):
    with client_for(tmp_path) as client:
        first=apply_d1(client); duplicate=apply_d1(client)
        assert first.status_code==200 and duplicate.json()["event_result"]["disposition"]=="duplicate"
        fixture=load_fixture(Path(__file__).parents[4]); command=fixture.replay_events[0].model_dump(mode="json")
        command["new_arrival_at"]="2026-09-26T18:31:00+05:30"
        conflict=client.post("/api/v1/trips/trip:mumbai-goa-v2/events",json=command)
        assert conflict.status_code==409 and conflict.json()["error"]["code"]=="EVENT_ID_CONFLICT"
        command["event_id"]="event:stale"
        stale=client.post("/api/v1/trips/trip:mumbai-goa-v2/events",json=command)
        assert stale.status_code==409 and stale.json()["error"]["code"]=="VERSION_CONFLICT"
        assert client.get("/api/v1/trips/trip:mumbai-goa-v2").json()["snapshot"]["trip"]["version"]==2


def test_t23_noop_and_guarded_itinerary_edit(tmp_path):
    with client_for(tmp_path) as client:
        snapshot=client.get("/api/v1/trips/trip:mumbai-goa-v2").json()["snapshot"]
        itinerary=snapshot["trip"]["active_itinerary"]
        noop=client.put("/api/v1/trips/trip:mumbai-goa-v2/itinerary",json=edit_command(snapshot,version=1))
        assert noop.status_code==200 and noop.json()["changed"] is False
        itinerary["activities"]=[item for item in itinerary["activities"] if item["id"]!="act:H1"]
        denied=client.put("/api/v1/trips/trip:mumbai-goa-v2/itinerary",json=edit_command(snapshot,version=1,itinerary=itinerary))
        assert denied.status_code==409 and denied.json()["error"]["code"]=="HARD_CHANGE_ACKNOWLEDGEMENT_REQUIRED"


def test_api26_edit_preserves_authoritative_immutable_state(tmp_path):
    with client_for(tmp_path) as client:
        before=client.get("/api/v1/trips/trip:mumbai-goa-v2").json()["snapshot"]
        itinerary=json.loads(json.dumps(before["trip"]["active_itinerary"]))
        itinerary["dependencies"][0]["buffer_sec"] += 1
        response=client.put("/api/v1/trips/trip:mumbai-goa-v2/itinerary",json=edit_command(before,version=1,itinerary=itinerary,suffix="api26"))
        assert response.status_code==200
        after=response.json()["snapshot"]
        for field in ("original_itinerary","effective_services","bookings"):
            assert after["trip"][field]==before["trip"][field]
        assert after["catalog"]==before["catalog"]
        forbidden=edit_command(before,version=1) | {"original_itinerary":before["trip"]["original_itinerary"]}
        assert client.put("/api/v1/trips/trip:mumbai-goa-v2/itinerary",json=forbidden).status_code==422

        fixture=load_fixture(Path(__file__).parents[4])
        completed_provenance=fixture.trip_provenance[0].model_copy(update={"id":"prov:user:completed-state","source_ref":"user-action:completed-state"})
        completed_state={**after["trip"]["current_state"],"location_id":"rail:MAO","phase":"at_location","active_service_id":None,"completed_activity_ids":["act:T1"],"next_recovery_point_id":None,"provenance_id":completed_provenance.id}
        state_response=client.put("/api/v1/trips/trip:mumbai-goa-v2/current-state",json={"expected_trip_version":2,"current_state":completed_state,"provenance":completed_provenance.model_dump(mode="json")})
        assert state_response.status_code==200
        completed_snapshot=state_response.json()["snapshot"]
        changed_prefix=json.loads(json.dumps(completed_snapshot["trip"]["active_itinerary"]))
        next(item for item in changed_prefix["activities"] if item["id"]=="act:T1")["hard"]=False
        completed_edit=client.put("/api/v1/trips/trip:mumbai-goa-v2/itinerary",json=edit_command(completed_snapshot,version=3,itinerary=changed_prefix,suffix="api26-completed"))
        assert completed_edit.status_code==409 and completed_edit.json()["error"]["code"]=="COMPLETED_ACTIVITY_IMMUTABLE"

        onboard_provenance=fixture.trip_provenance[0].model_copy(update={"id":"prov:user:onboard-state","source_ref":"user-action:onboard-state"})
        onboard_state={**completed_state,"location_id":None,"phase":"onboard","active_service_id":"svc:T1:2026-09-26","completed_activity_ids":[],"next_recovery_point_id":"rail:MAO","provenance_id":onboard_provenance.id}
        onboard_response=client.put("/api/v1/trips/trip:mumbai-goa-v2/current-state",json={"expected_trip_version":3,"current_state":onboard_state,"provenance":onboard_provenance.model_dump(mode="json")})
        assert onboard_response.status_code==200
        onboard_snapshot=onboard_response.json()["snapshot"]
        changed_active=json.loads(json.dumps(onboard_snapshot["trip"]["active_itinerary"]))
        next(item for item in changed_active["activities"] if item["id"]=="act:T1")["hard"]=False
        active_edit=client.put("/api/v1/trips/trip:mumbai-goa-v2/itinerary",json=edit_command(onboard_snapshot,version=4,itinerary=changed_active,suffix="api26-active"))
        assert active_edit.status_code==409 and active_edit.json()["error"]["code"]=="ACTIVE_ACTIVITY_IMMUTABLE"


def test_api27_hard_removal_requires_literal_acknowledgement(tmp_path):
    with client_for(tmp_path) as client:
        snapshot=client.get("/api/v1/trips/trip:mumbai-goa-v2").json()["snapshot"]
        itinerary=json.loads(json.dumps(snapshot["trip"]["active_itinerary"]))
        itinerary["activities"]=[item for item in itinerary["activities"] if item["id"]!="act:H1"]
        itinerary["dependencies"]=[item for item in itinerary["dependencies"] if "H1" not in item["id"]]
        template=next(item for item in snapshot["trip"]["active_itinerary"]["dependencies"] if item["id"]=="dep:C1-to-H1")
        itinerary["dependencies"].append({**template,"id":"dep:C1-to-C2","from_id":"act:C1","to_id":"act:C2"})
        constraints=json.loads(json.dumps(snapshot["trip"]["constraints"]))
        constraints["required_commitment_ids"]=["act:E1"]
        denied=client.put("/api/v1/trips/trip:mumbai-goa-v2/itinerary",json=edit_command(snapshot,version=1,itinerary=itinerary,constraints=constraints,suffix="api27-denied"))
        assert denied.status_code==409 and denied.json()["error"]["code"]=="HARD_CHANGE_ACKNOWLEDGEMENT_REQUIRED"
        non_literal=edit_command(snapshot,version=1,itinerary=itinerary,constraints=constraints,acknowledge=True,suffix="api27-non-literal")
        non_literal["acknowledge_hard_changes"]="true"
        assert client.put("/api/v1/trips/trip:mumbai-goa-v2/itinerary",json=non_literal).status_code==422
        accepted=client.put("/api/v1/trips/trip:mumbai-goa-v2/itinerary",json=edit_command(snapshot,version=1,itinerary=itinerary,constraints=constraints,acknowledge=True,suffix="api27-accepted"))
        assert accepted.status_code==200 and accepted.json()["mutation_kind"]=="itinerary_edit"
        assert accepted.json()["snapshot"]["trip"]["constraints"]==constraints


def test_api28_material_edit_versions_stales_and_identical_is_noop(tmp_path):
    with client_for(tmp_path) as client:
        apply_d1(client); generate(client)
        snapshot=client.get("/api/v1/trips/trip:mumbai-goa-v2").json()["snapshot"]
        itinerary=json.loads(json.dumps(snapshot["trip"]["active_itinerary"]))
        itinerary["dependencies"][0]["buffer_sec"] += 1
        changed=client.put("/api/v1/trips/trip:mumbai-goa-v2/itinerary",json=edit_command(snapshot,version=2,itinerary=itinerary,suffix="api28"))
        assert changed.status_code==200
        assert (changed.json()["prior_trip_version"],changed.json()["current_trip_version"],changed.json()["changed"])==(2,3,True)
        assert changed.json()["staled_plan_count"]>0
        assert client.get("/api/v1/trips/trip:mumbai-goa-v2/plans/plan:F3:v2").json()["lifecycle_status"]=="stale"
        current=changed.json()["snapshot"]
        noop=client.put("/api/v1/trips/trip:mumbai-goa-v2/itinerary",json=edit_command(current,version=3,suffix="api28-noop"))
        assert noop.status_code==200
        assert (noop.json()["prior_trip_version"],noop.json()["current_trip_version"],noop.json()["changed"],noop.json()["staled_plan_count"])==(3,3,False,0)


def test_api29_dependency_dag_and_commitment_order_must_agree(tmp_path):
    with client_for(tmp_path) as client:
        snapshot=client.get("/api/v1/trips/trip:mumbai-goa-v2").json()["snapshot"]
        reversed_constraints=json.loads(json.dumps(snapshot["trip"]["constraints"]))
        reversed_constraints["required_commitment_ids"]=["act:E1","act:H1"]
        mismatch=client.put("/api/v1/trips/trip:mumbai-goa-v2/itinerary",json=edit_command(snapshot,version=1,constraints=reversed_constraints,suffix="api29-order"))
        assert mismatch.status_code==422 and mismatch.json()["error"]["code"]=="ITINERARY_EDIT_INVALID"
        cyclic=json.loads(json.dumps(snapshot["trip"]["active_itinerary"]))
        cyclic["dependencies"].append({"id":"dep:E1-to-T1","from_id":"act:E1","to_id":"act:T1","buffer_sec":0,"reason":"invalid cycle"})
        cycle=client.put("/api/v1/trips/trip:mumbai-goa-v2/itinerary",json=edit_command(snapshot,version=1,itinerary=cyclic,suffix="api29-cycle"))
        assert cycle.status_code==422 and cycle.json()["error"]["code"]=="ITINERARY_EDIT_INVALID"


def test_t24_t27_contract_safety_and_cross_trip_plan_ownership(tmp_path):
    with client_for(tmp_path) as client:
        assert client.post("/api/v1/trips",content="{}",headers={"content-type":"text/plain"}).status_code==415
        oversized=client.post("/api/v1/trips",content=b"x"*262145,headers={"content-type":"application/json"})
        assert oversized.status_code==413 and oversized.json()["error"]["code"]=="REQUEST_TOO_LARGE"
        invalid=client.post("/api/v1/trips",json={"source_type":"fixture","scenario_id":"mumbai-goa-v2","display_name":None,"unknown":1})
        assert invalid.status_code==422 and invalid.json()["error"]["code"]=="VALIDATION_ERROR"
        apply_d1(client); generate(client)
        created=client.post("/api/v1/trips",json={"source_type":"fixture","scenario_id":"mumbai-goa-v2","display_name":"Second"}).json()
        cross=client.get(f"/api/v1/trips/{created['trip_id']}/plans/plan:F3:v2")
        assert cross.status_code==404 and cross.json()["error"]["code"]=="PLAN_NOT_FOUND"


def test_t28_hash_corruption_stops_snapshot_read(tmp_path):
    database=tmp_path/"a3.sqlite3"
    with client_for(tmp_path) as client:
        client.get("/api/v1/trips/trip:mumbai-goa-v2")
    with connect(database) as connection:
        connection.execute("UPDATE trip_versions SET snapshot_hash='bad' WHERE trip_id='trip:mumbai-goa-v2' AND version=1")
    with connect(database) as connection:
        from resilitrip.infrastructure.repositories import TripRepository
        import pytest
        with pytest.raises(RuntimeError,match="INTERNAL_DATA_INTEGRITY_ERROR"):
            TripRepository(connection).get_current("trip:mumbai-goa-v2")


def test_t19_cancellation_and_event_sequence_contract(tmp_path):
    with client_for(tmp_path) as client:
        fixture = load_fixture(Path(__file__).parents[4])
        source = fixture.replay_events[0]
        cancellation = {
            "event_id": "event:T1-cancelled",
            "source_id": source.source_id,
            "source_sequence": 1,
            "expected_trip_version": 1,
            "type": "SERVICE_CANCELLED",
            "service_id": source.service_id,
            "observed_at": source.observed_at.isoformat(),
            "effective_at": source.effective_at.isoformat(),
            "provenance": source.provenance.model_copy(
                update={"id": "prov:replay:T1-cancelled"}
            ).model_dump(mode="json"),
        }
        response = client.post("/api/v1/trips/trip:mumbai-goa-v2/events", json=cancellation)
        assert response.status_code == 200
        states = response.json()["event_result"]["snapshot"]["trip"]["effective_services"]
        assert next(item for item in states if item["service_id"] == source.service_id)["status"] == "cancelled"
        plans = generate(client).json()["planner_result"]
        assert {item["id"] for item in plans["feasible_plans"]} == {"plan:F2:v2", "plan:F3:v2"}

        later = cancellation | {
            "event_id": "event:old-sequence",
            "expected_trip_version": 2,
        }
        stale = client.post("/api/v1/trips/trip:mumbai-goa-v2/events", json=later)
        assert stale.status_code == 409
        assert stale.json()["error"]["code"] == "EVENT_SEQUENCE_STALE"


def test_t20_concurrent_event_serialization_and_rollback(tmp_path, monkeypatch):
    database = tmp_path / "a3.sqlite3"
    app = create_app(Settings(database_path=database))
    with TestClient(app) as client:
        fixture = load_fixture(Path(__file__).parents[4])
        command = fixture.replay_events[0].model_dump(mode="json")
        with ThreadPoolExecutor(max_workers=2) as pool:
            responses = list(pool.map(lambda _: client.post(
                "/api/v1/trips/trip:mumbai-goa-v2/events", json=command
            ), range(2)))
        assert sorted(response.json()["event_result"]["disposition"] for response in responses) == ["applied", "duplicate"]
        assert all(response.status_code == 200 for response in responses)

    rollback_database = tmp_path / "rollback.sqlite3"
    rollback_app = create_app(Settings(database_path=rollback_database))
    original = TripRepository.save_version

    def fail_before_commit(self, prior_version, trip):
        raise RuntimeError("injected failure")

    with TestClient(rollback_app, raise_server_exceptions=False) as client:
        monkeypatch.setattr(TripRepository, "save_version", fail_before_commit)
        response = apply_d1(client)
        assert response.status_code == 500
        monkeypatch.setattr(TripRepository, "save_version", original)
        assert client.get("/api/v1/trips/trip:mumbai-goa-v2").json()["snapshot"]["trip"]["version"] == 1
    with connect(rollback_database) as connection:
        assert connection.execute("SELECT COUNT(*) FROM events").fetchone()[0] == 0

    conflict_database = tmp_path / "conflict.sqlite3"
    conflict_app = create_app(Settings(database_path=conflict_database))
    with TestClient(conflict_app) as client:
        fixture = load_fixture(Path(__file__).parents[4])
        first = fixture.replay_events[0].model_dump(mode="json")
        second = first | {"event_id": "event:concurrent-other", "source_sequence": 2}
        with ThreadPoolExecutor(max_workers=2) as pool:
            responses = list(pool.map(
                lambda body: client.post("/api/v1/trips/trip:mumbai-goa-v2/events", json=body),
                (first, second),
            ))
        assert sorted(response.status_code for response in responses) == [200, 409]
        assert next(response for response in responses if response.status_code == 409).json()["error"]["code"] == "VERSION_CONFLICT"
        assert client.get("/api/v1/trips/trip:mumbai-goa-v2").json()["snapshot"]["trip"]["version"] == 2


def test_t20_planner_and_adoption_failures_roll_back_all_writes(tmp_path, monkeypatch):
    planner_database = tmp_path / "planner-rollback.sqlite3"
    app = create_app(Settings(database_path=planner_database))
    original_save = PlanRepository.save_result

    def fail_after_plan_rows(self, result):
        original_save(self, result)
        raise RuntimeError("injected planner persistence failure")

    with TestClient(app, raise_server_exceptions=False) as client:
        apply_d1(client)
        monkeypatch.setattr(PlanRepository, "save_result", fail_after_plan_rows)
        assert generate(client).status_code == 500
        monkeypatch.setattr(PlanRepository, "save_result", original_save)
    with connect(planner_database) as connection:
        assert connection.execute("SELECT COUNT(*) FROM planner_runs").fetchone()[0] == 0
        assert connection.execute("SELECT COUNT(*) FROM plans").fetchone()[0] == 0

    adoption_database = tmp_path / "adoption-rollback.sqlite3"
    adoption_app = create_app(Settings(database_path=adoption_database))
    original_add = AdoptionRepository.add

    def fail_after_adoption_changes(self, record):
        raise RuntimeError("injected adoption persistence failure")

    with TestClient(adoption_app, raise_server_exceptions=False) as client:
        apply_d1(client)
        generate(client)
        monkeypatch.setattr(AdoptionRepository, "add", fail_after_adoption_changes)
        failed = client.post("/api/v1/trips/trip:mumbai-goa-v2/adoptions", json={
            "expected_trip_version": 2, "plan_id": "plan:F3:v2", "acknowledge_simulation": True,
        })
        assert failed.status_code == 500
        monkeypatch.setattr(AdoptionRepository, "add", original_add)
        assert client.get("/api/v1/trips/trip:mumbai-goa-v2").json()["snapshot"]["trip"]["version"] == 2
        assert client.get("/api/v1/trips/trip:mumbai-goa-v2/plans/plan:F3:v2").json()["lifecycle_status"] == "preview"
    with connect(adoption_database) as connection:
        assert connection.execute("SELECT COUNT(*) FROM adoptions").fetchone()[0] == 0
