from resilitrip.application.snapshots import create_initial_trip
from resilitrip.infrastructure.repositories import TripRepository, canonical_json, content_hash, snapshot_hash, seed_catalog
from resilitrip.infrastructure.sqlite import connect, initialize


def test_initial_trip_persists_as_version_one(tmp_path, hero_fixture) -> None:
    database_path = tmp_path / "resilitrip.sqlite3"
    initialize(database_path)
    with connect(database_path) as connection:
        seed_catalog(connection, hero_fixture.catalog)
        trip = create_initial_trip(hero_fixture)
        repository = TripRepository(connection)
        repository.create_initial(trip)
        loaded = repository.get_initial(trip.id)

    assert loaded.version == 1
    assert loaded.catalog_version == "catalog:mumbai-goa-v2"
    assert loaded.baseline_remaining_spend_paise == 130_000


def test_r1_migration_marks_legacy_rows_active_without_rewriting_snapshot_or_hash(tmp_path, hero_fixture) -> None:
    database_path = tmp_path / "legacy.sqlite3"
    with connect(database_path) as connection:
        connection.execute("CREATE TABLE schema_migrations (revision TEXT PRIMARY KEY, applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)")
        connection.execute("INSERT INTO schema_migrations (revision) VALUES ('a1_initial_schema'), ('a3_backend_schema')")
        connection.execute("CREATE TABLE catalogs (catalog_version TEXT PRIMARY KEY, scenario_id TEXT NOT NULL, canonical_json TEXT NOT NULL, snapshot_hash TEXT NOT NULL UNIQUE)")
        connection.execute("CREATE TABLE trips (trip_id TEXT PRIMARY KEY, current_version INTEGER NOT NULL, catalog_version TEXT NOT NULL, scenario_id TEXT NOT NULL, FOREIGN KEY(catalog_version) REFERENCES catalogs(catalog_version))")
        connection.execute("CREATE TABLE trip_versions (trip_id TEXT NOT NULL, version INTEGER NOT NULL, snapshot_json TEXT NOT NULL, snapshot_hash TEXT NOT NULL, mutation_kind TEXT NOT NULL, PRIMARY KEY(trip_id, version), FOREIGN KEY(trip_id) REFERENCES trips(trip_id))")
        seed_catalog(connection, hero_fixture.catalog)
        trip = create_initial_trip(hero_fixture)
        legacy_snapshot = trip.model_dump(mode="json")
        legacy_snapshot.pop("lifecycle")
        payload = canonical_json(legacy_snapshot)
        original = (payload, content_hash(legacy_snapshot))
        connection.execute("INSERT INTO trips VALUES (?,?,?,?)", (trip.id, trip.version, trip.catalog_version, trip.scenario_id))
        connection.execute("INSERT INTO trip_versions VALUES (?,?,?,?,?)", (trip.id, trip.version, *original, "created"))

    initialize(database_path)
    with connect(database_path) as connection:
        migrated = connection.execute("SELECT trip_mode,trip_lifecycle FROM trips WHERE trip_id=?", (trip.id,)).fetchone()
        preserved = connection.execute(
            "SELECT snapshot_json, snapshot_hash FROM trip_versions WHERE trip_id=? AND version=1", (trip.id,)
        ).fetchone()
        loaded = TripRepository(connection).get_initial(trip.id)

    assert migrated == ("demo", "active")
    assert preserved == original
    assert str(loaded.mode) == "demo"
    assert str(loaded.lifecycle) == "active"


def test_r1_repository_loads_real_drafts_outside_the_demo_namespace(tmp_path, hero_fixture) -> None:
    database_path = tmp_path / "real-trip.sqlite3"
    initialize(database_path)
    demo_trip = create_initial_trip(hero_fixture)
    real_trip = demo_trip.model_validate({
        **demo_trip.model_dump(mode="json"),
        "id": "trip:real-example",
        "scenario_id": None,
        "mode": "real",
        "lifecycle": "draft",
        "truth_label": "REAL TRIP — FACTS MAY BE UNKNOWN",
    })
    with connect(database_path) as connection:
        seed_catalog(connection, hero_fixture.catalog)
        repository = TripRepository(connection)
        repository.create_initial(real_trip)
        stored_mode = connection.execute("SELECT trip_mode,trip_lifecycle FROM trips WHERE trip_id=?", (real_trip.id,)).fetchone()
        loaded = repository.get_initial(real_trip.id)

    assert stored_mode == ("real", "draft")
    assert str(loaded.mode) == "real"
    assert str(loaded.lifecycle) == "draft"
    assert loaded.scenario_id is None
