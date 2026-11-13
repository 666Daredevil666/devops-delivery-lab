import psycopg
import pytest


def test_repeated_migration_preserves_data(client, database_dsn):
    from app.migrate import run_migrations

    note = client.post("/notes", json={"title": "Keep", "content": "persistent"}).json()
    run_migrations(database_dsn)
    run_migrations(database_dsn)
    assert client.get(f"/notes/{note['id']}").json() == note
    with psycopg.connect(database_dsn) as connection:
        versions = connection.execute("SELECT version FROM schema_migrations").fetchall()
    assert versions == [("001_create_notes.sql",)]


def test_failed_migration_rolls_back_ddl_and_version(database_dsn, tmp_path, monkeypatch):
    from app import migrate

    (tmp_path / "999_invalid.sql").write_text(
        "CREATE TABLE should_rollback (id integer); SELECT missing_column;"
    )
    monkeypatch.setattr(migrate, "MIGRATIONS_DIR", tmp_path)
    with pytest.raises(psycopg.Error):
        migrate.run_migrations(database_dsn)
    with psycopg.connect(database_dsn) as connection:
        assert connection.execute("SELECT to_regclass('should_rollback')").fetchone() == (None,)
        assert connection.execute(
            "SELECT count(*) FROM schema_migrations WHERE version = '999_invalid.sql'"
        ).fetchone() == (0,)
