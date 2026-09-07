from resilitrip.infrastructure.sqlite import connect, initialize


def test_sqlite_enables_foreign_keys_wal_and_busy_timeout(tmp_path) -> None:
    database_path = tmp_path / "resilitrip.sqlite3"
    initialize(database_path)

    with connect(database_path) as connection:
        foreign_keys = connection.execute("PRAGMA foreign_keys").fetchone()[0]
        journal_mode = connection.execute("PRAGMA journal_mode").fetchone()[0]
        busy_timeout = connection.execute("PRAGMA busy_timeout").fetchone()[0]

    assert foreign_keys == 1
    assert journal_mode.lower() == "wal"
    assert busy_timeout == 5_000
