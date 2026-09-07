"""Health contract endpoints."""

from fastapi import APIRouter, Request
from resilitrip.api.contracts import LiveHealthResponse, ReadyHealthResponse


router = APIRouter(tags=["health"])


@router.get("/health/live", operation_id="health_live", response_model=LiveHealthResponse)
def liveness() -> LiveHealthResponse:
    return LiveHealthResponse()


@router.get("/health/ready", operation_id="health_ready", response_model=ReadyHealthResponse)
def readiness(request: Request) -> ReadyHealthResponse:
    from resilitrip.infrastructure.sqlite import connect
    with connect(request.app.state.settings.database_path) as connection:
        revision=connection.execute("SELECT revision FROM schema_migrations ORDER BY rowid DESC LIMIT 1").fetchone()[0]
        count=connection.execute("SELECT COUNT(DISTINCT scenario_id) FROM catalogs WHERE scenario_id<>'manual'").fetchone()[0]
    return ReadyHealthResponse(schema_revision=revision, installed_scenario_count=count)
