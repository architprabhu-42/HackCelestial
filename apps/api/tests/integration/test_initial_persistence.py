from resilitrip.application.snapshots import create_initial_trip
from resilitrip.infrastructure.repositories import TripRepository, seed_catalog
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
