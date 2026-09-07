"""FastAPI application factory for the modular monolith."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from uuid import uuid4
import re
from contextlib import asynccontextmanager
from pathlib import Path

from resilitrip.api.routers.health import router as health_router
from resilitrip.api.routers.contracts import router as contracts_router
from resilitrip.config import default_settings
from resilitrip.application.snapshots import create_initial_trip
from resilitrip.infrastructure.fixture_loader import load_fixture
from resilitrip.infrastructure.repositories import TripRepository, seed_catalog
from resilitrip.infrastructure.sqlite import connect
from resilitrip.infrastructure.sqlite import initialize
from resilitrip.api.errors import ApiProblem, api_problem_handler, internal_error_handler, problem_body, validation_handler


def _install_openapi_examples(app: FastAPI) -> None:
    """Attach the eight executable examples required by Document 07 section 39.3."""
    generated = app.openapi

    def documented_openapi():
        if app.openapi_schema is not None:
            return app.openapi_schema
        schema = generated()
        paths = schema["paths"]
        fixture_create = {"source_type":"fixture","scenario_id":"mumbai-goa-v2","display_name":"Asha"}
        provenance = {"id":"prov:replay:D1","kind":"synthetic","verification":"fixture","observed_at":"2026-09-26T05:00:00+05:30","retrieved_at":"2026-09-26T05:00:00+05:30","valid_until":None,"source_ref":"replay:mumbai-goa-v2"}
        d1 = {"event_id":"event:D1","source_id":"replay:mumbai-goa-v2","source_sequence":1,"expected_trip_version":1,"type":"SERVICE_TIMING_UPDATED","service_id":"svc:T1:2026-09-26","observed_at":"2026-09-26T05:00:00+05:30","effective_at":"2026-09-26T05:00:00+05:30","new_departure_at":"2026-09-26T09:00:00+05:30","new_arrival_at":"2026-09-26T18:30:00+05:30","provenance":provenance}
        cancellation = {key:value for key,value in d1.items() if key not in {"new_departure_at","new_arrival_at"}}
        cancellation.update({"event_id":"event:T1-cancelled","type":"SERVICE_CANCELLED"})
        constraints = {"party_size":1,"max_cash_required_paise":700000,"max_incremental_cost_paise":900000,"allowed_modes":["rail","air","road_transfer"],"required_commitment_ids":["act:H1","act:E1"],"accessibility_required":False,"ranking_preset":"cheapest","max_new_fixed_legs":2,"max_transfer_legs":8,"horizon_end":"2026-09-27T05:00:00+05:30","risk_threshold_sec":1800}
        replacement_provenance = {**provenance,"id":"prov:user:budget-7000","kind":"user_reported","source_ref":"user-budget-update"}
        examples = {
            ("/api/v1/trips","post"): {"fixture_creation":{"value":fixture_create}},
            ("/api/v1/trips/{trip_id}/events","post"): {"d1_timing":{"value":d1},"service_cancellation":{"value":cancellation}},
            ("/api/v1/trips/{trip_id}/constraints","put"): {"budget_7000":{"value":{"expected_trip_version":2,"constraints":constraints,"provenance":replacement_provenance}}},
            ("/api/v1/trips/{trip_id}/plans","post"): {"hero_planner":{"value":{"expected_trip_version":2,"expected_catalog_version":"catalog:mumbai-goa-v2","ranking_preset":"cheapest"}}},
            ("/api/v1/trips/{trip_id}/adoptions","post"): {"f3_adoption":{"value":{"expected_trip_version":2,"plan_id":"plan:F3:v2","acknowledge_simulation":True}}},
        }
        for (path, method), values in examples.items():
            paths[path][method]["requestBody"]["content"]["application/json"]["examples"] = values
        problem_base = {"message":"The trip changed. Refresh and try again.","request_id":"req_example","retryable":True,"field_errors":[],"current_trip_version":3,"current_catalog_version":"catalog:mumbai-goa-v2"}
        paths["/api/v1/trips/{trip_id}/constraints"]["put"]["responses"]["409"]["content"]["application/json"]["examples"] = {"version_conflict":{"value":{"error":{"code":"VERSION_CONFLICT",**problem_base}}}}
        validation = {"code":"VALIDATION_ERROR","message":"The request did not satisfy the API contract.","request_id":"req_example","retryable":False,"field_errors":[{"path":"/constraints/max_cash_required_paise","code":"INVALID_MONEY","message":"Invalid request field.","rejected_value":None}],"current_trip_version":None,"current_catalog_version":None}
        paths["/api/v1/trips/{trip_id}/constraints"]["put"]["responses"]["422"]["content"]["application/json"]["examples"] = {"field_validation":{"value":{"error":validation}}}
        app.openapi_schema = schema
        return schema

    app.openapi = documented_openapi


def create_app(settings=None) -> FastAPI:
    configured_settings = settings or default_settings()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        initialize(configured_settings.database_path)
        fixture = load_fixture(__import__("pathlib").Path(__file__).resolve().parents[3])
        with connect(configured_settings.database_path) as connection:
            seed_catalog(connection, fixture.catalog)
            repository = TripRepository(connection)
            trip = create_initial_trip(fixture)
            if not repository.exists(trip.id):
                repository.create_initial(trip)
        yield

    app = FastAPI(title="ResiliTrip API", version="resilitrip-api-1.0", openapi_url="/api/v1/openapi.json", lifespan=lifespan)
    app.state.settings = configured_settings
    app.add_exception_handler(ApiProblem, api_problem_handler)
    app.add_exception_handler(RequestValidationError, validation_handler)
    app.add_exception_handler(Exception, internal_error_handler)

    @app.middleware("http")
    async def contract_guard(request: Request, call_next):
        supplied_request_id = request.headers.get("X-Request-ID")
        request.state.request_id = (
            supplied_request_id
            if supplied_request_id and re.fullmatch(r"[A-Za-z0-9._:-]{1,128}", supplied_request_id)
            else f"req_{uuid4().hex}"
        )
        if request.method in {"POST","PUT","PATCH"}:
            length=int(request.headers.get("content-length","0") or 0)
            if length > 262144:
                return JSONResponse(status_code=413,content=problem_body(request,"REQUEST_TOO_LARGE","The request body exceeds 262144 bytes."))
            media=request.headers.get("content-type","").split(";",1)[0].lower()
            if media != "application/json":
                return JSONResponse(status_code=415,content=problem_body(request,"UNSUPPORTED_MEDIA_TYPE","Use application/json."))
        control = request.headers.get("X-ResiliTrip-Test-Control")
        if app.state.settings.allow_test_controls and control == "planner_error" and request.url.path.endswith("/plans"):
            return JSONResponse(status_code=503, content=problem_body(request, "TEST_BACKEND_FAILURE", "The local test service is temporarily unavailable."))
        response=await call_next(request)
        response.headers["X-Request-ID"]=request.state.request_id
        if response.headers.get("content-type", "").startswith("application/json"):
            response.headers["Content-Type"] = "application/json; charset=utf-8"
        if request.url.path.startswith("/api/v1/trips"):
            response.headers["Cache-Control"]="no-store"
            trip_id = request.scope.get("path_params", {}).get("trip_id")
            if trip_id and response.status_code < 400:
                try:
                    with connect(app.state.settings.database_path) as connection:
                        trip = TripRepository(connection).get_current(trip_id)
                    response.headers["ETag"] = (
                        f'W/"trip:{trip.id}:v{trip.version}:catalog:{trip.catalog_version}"'
                    )
                except (KeyError, RuntimeError):
                    pass
        return response

    app.include_router(health_router, prefix="/api")
    app.include_router(contracts_router, prefix="/api")
    frontend_dist = Path(__file__).resolve().parents[3] / "apps" / "web" / "dist"
    if frontend_dist.is_dir():
        app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
    _install_openapi_examples(app)
    return app


app = create_app()
