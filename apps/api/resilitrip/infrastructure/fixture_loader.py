"""Load only approved, executable scenario fixtures."""

from __future__ import annotations

from pathlib import Path

from pydantic import ValidationError

from resilitrip.domain.models import ExecutableScenarioFixture
from resilitrip.domain.validation import DomainValidationError, validate_fixture


class FixtureLoadError(ValueError):
    pass


def fixture_path(repository_root: Path, scenario_id: str) -> Path:
    if scenario_id != "mumbai-goa-v2":
        raise FixtureLoadError("SCENARIO_NOT_FOUND")
    return repository_root / "data" / "fixtures" / "mumbai-goa-v2.json"


def load_fixture(repository_root: Path, scenario_id: str = "mumbai-goa-v2") -> ExecutableScenarioFixture:
    path = fixture_path(repository_root, scenario_id)
    try:
        fixture = ExecutableScenarioFixture.model_validate_json(path.read_bytes())
        validate_fixture(fixture)
    except (OSError, ValidationError, DomainValidationError) as error:
        raise FixtureLoadError(str(error)) from error
    return fixture
