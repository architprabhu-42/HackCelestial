from fastapi.testclient import TestClient
import networkx
import pydantic
import sqlalchemy

from resilitrip.main import create_app


def test_direct_dependency_imports() -> None:
    assert fastapi_version().startswith("0.115.")
    assert pydantic.VERSION.startswith("2.")
    assert sqlalchemy.__version__.startswith("2.")
    assert networkx.__version__.startswith("3.")


def fastapi_version() -> str:
    import fastapi

    return fastapi.__version__


def test_liveness_endpoint() -> None:
    with TestClient(create_app()) as client:
        response = client.get("/api/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "resilitrip", "contract_version": "resilitrip-api-1.0"}
