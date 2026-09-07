from pathlib import Path

import pytest

from resilitrip.infrastructure.fixture_loader import load_fixture


@pytest.fixture
def repository_root() -> Path:
    return Path(__file__).resolve().parents[3]


@pytest.fixture
def hero_fixture(repository_root: Path):
    return load_fixture(repository_root)
