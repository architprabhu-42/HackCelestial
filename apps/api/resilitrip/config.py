"""Configuration for the local-only P0 application."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    """Settings intentionally limited to the Gate A0 infrastructure needs."""

    database_path: Path
    allow_test_controls: bool = False


def default_settings() -> Settings:
    repository_root = Path(__file__).resolve().parents[3]
    database_path = Path(os.environ.get("RESILITRIP_DATABASE_PATH", repository_root / "data" / "local" / "resilitrip.sqlite3"))
    return Settings(database_path=database_path, allow_test_controls=os.environ.get("RESILITRIP_TEST_CONTROLS") == "1")
