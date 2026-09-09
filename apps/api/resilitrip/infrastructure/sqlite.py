"""SQLite connection setup shared by the application and integration tests."""

from __future__ import annotations

import sqlite3
from pathlib import Path


BUSY_TIMEOUT_MS = 5_000


def _initial_schema(connection: sqlite3.Connection) -> None:
    """Install the historical A1/A3 schema for an empty database only."""
    connection.execute("CREATE TABLE IF NOT EXISTS catalogs (catalog_version TEXT PRIMARY KEY, scenario_id TEXT NOT NULL, canonical_json TEXT NOT NULL, snapshot_hash TEXT NOT NULL UNIQUE)")
    connection.execute("CREATE TABLE IF NOT EXISTS trips (trip_id TEXT PRIMARY KEY, current_version INTEGER NOT NULL, catalog_version TEXT NOT NULL, scenario_id TEXT NOT NULL, FOREIGN KEY(catalog_version) REFERENCES catalogs(catalog_version))")
    connection.execute("CREATE TABLE IF NOT EXISTS trip_versions (trip_id TEXT NOT NULL, version INTEGER NOT NULL, snapshot_json TEXT NOT NULL, snapshot_hash TEXT NOT NULL, mutation_kind TEXT NOT NULL, PRIMARY KEY(trip_id, version), FOREIGN KEY(trip_id) REFERENCES trips(trip_id))")
    connection.execute("CREATE TABLE IF NOT EXISTS events (trip_id TEXT NOT NULL, event_id TEXT NOT NULL, source_id TEXT NOT NULL, source_sequence INTEGER NOT NULL, command_json TEXT NOT NULL, command_hash TEXT NOT NULL, applied_version INTEGER NOT NULL, PRIMARY KEY(trip_id,event_id), UNIQUE(trip_id,source_id,source_sequence), FOREIGN KEY(trip_id) REFERENCES trips(trip_id))")
    connection.execute("CREATE TABLE IF NOT EXISTS planner_runs (run_id TEXT PRIMARY KEY, trip_id TEXT NOT NULL, trip_version INTEGER NOT NULL, catalog_version TEXT NOT NULL, result_json TEXT NOT NULL, result_hash TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY(trip_id) REFERENCES trips(trip_id))")
    connection.execute("CREATE TABLE IF NOT EXISTS plans (trip_id TEXT NOT NULL, plan_id TEXT NOT NULL, trip_version INTEGER NOT NULL, catalog_version TEXT NOT NULL, plan_json TEXT NOT NULL, plan_hash TEXT NOT NULL, lifecycle_status TEXT NOT NULL, search_complete INTEGER NOT NULL, PRIMARY KEY(trip_id,plan_id), FOREIGN KEY(trip_id) REFERENCES trips(trip_id))")
    connection.execute("CREATE TABLE IF NOT EXISTS adoptions (adoption_id TEXT PRIMARY KEY, trip_id TEXT NOT NULL, plan_id TEXT NOT NULL, prior_version INTEGER NOT NULL, resulting_version INTEGER NOT NULL, record_json TEXT NOT NULL, record_hash TEXT NOT NULL, FOREIGN KEY(trip_id) REFERENCES trips(trip_id), FOREIGN KEY(trip_id,plan_id) REFERENCES plans(trip_id,plan_id))")


def _r1_trip_mode_namespace(connection: sqlite3.Connection) -> None:
    """Add an explicit namespace without altering historical trip snapshots."""
    columns = {row[1] for row in connection.execute("PRAGMA table_info(trips)")}
    if "trip_mode" not in columns:
        connection.execute("ALTER TABLE trips ADD COLUMN trip_mode TEXT NOT NULL DEFAULT 'demo' CHECK(trip_mode IN ('demo', 'real'))")


def _r1_trip_lifecycle(connection: sqlite3.Connection) -> None:
    """Add current-record lifecycle without changing immutable snapshots."""
    columns = {row[1] for row in connection.execute("PRAGMA table_info(trips)")}
    if "trip_lifecycle" not in columns:
        connection.execute("ALTER TABLE trips ADD COLUMN trip_lifecycle TEXT NOT NULL DEFAULT 'active' CHECK(trip_lifecycle IN ('draft', 'active'))")


def _r1_generic_trip_namespace(connection: sqlite3.Connection) -> None:
    """Install additive R1 generic-trip history without touching demo tables."""
    connection.execute(
        "CREATE TABLE IF NOT EXISTS generic_trips ("
        "trip_id TEXT PRIMARY KEY, current_version INTEGER NOT NULL, "
        "trip_mode TEXT NOT NULL CHECK(trip_mode IN ('demo', 'real')), "
        "trip_lifecycle TEXT NOT NULL CHECK(trip_lifecycle IN ('draft', 'active')), "
        "scenario_id TEXT, truth_label TEXT NOT NULL)"
    )
    connection.execute(
        "CREATE TABLE IF NOT EXISTS generic_trip_versions ("
        "trip_id TEXT NOT NULL, version INTEGER NOT NULL, snapshot_json TEXT NOT NULL, "
        "snapshot_hash TEXT NOT NULL, mutation_kind TEXT NOT NULL, "
        "PRIMARY KEY(trip_id, version), "
        "FOREIGN KEY(trip_id) REFERENCES generic_trips(trip_id))"
    )
    connection.execute(
        "CREATE TABLE IF NOT EXISTS generic_semantic_snapshots ("
        "trip_id TEXT NOT NULL, snapshot_id TEXT NOT NULL, trip_version INTEGER NOT NULL, "
        "snapshot_json TEXT NOT NULL, snapshot_hash TEXT NOT NULL, "
        "PRIMARY KEY(trip_id, snapshot_id), "
        "FOREIGN KEY(trip_id) REFERENCES generic_trips(trip_id))"
    )


MIGRATIONS: tuple[tuple[str, object], ...] = (
    ("a1_initial_schema", _initial_schema),
    ("a3_backend_schema", lambda _connection: None),
    ("r1_trip_mode_namespace", _r1_trip_mode_namespace),
    ("r1_trip_lifecycle", _r1_trip_lifecycle),
    ("r1_generic_trip_namespace", _r1_generic_trip_namespace),
)


def connect(database_path: Path) -> sqlite3.Connection:
    """Open SQLite with the mandatory foreign-key, WAL, and busy-timeout settings."""
    database_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database_path)
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute(f"PRAGMA busy_timeout = {BUSY_TIMEOUT_MS}")
    connection.execute("PRAGMA journal_mode = WAL")
    return connection


def initialize(database_path: Path) -> None:
    """Apply ordered, idempotent SQLite migrations without rewriting history."""
    with connect(database_path) as connection:
        connection.execute("CREATE TABLE IF NOT EXISTS schema_migrations (revision TEXT PRIMARY KEY, applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)")
        applied = {row[0] for row in connection.execute("SELECT revision FROM schema_migrations")}
        for revision, migration in MIGRATIONS:
            if revision in applied:
                continue
            migration(connection)
            connection.execute("INSERT INTO schema_migrations (revision) VALUES (?)", (revision,))
