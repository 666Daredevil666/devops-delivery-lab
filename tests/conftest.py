import os

import psycopg
import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def database_dsn():
    dsn = os.environ.get("TEST_DATABASE_URL")
    if not dsn:
        raise pytest.UsageError("Set TEST_DATABASE_URL to a dedicated database ending in _test")
    with psycopg.connect(dsn) as connection:
        name = connection.execute("SELECT current_database()").fetchone()[0]
        if not name.endswith("_test"):
            raise pytest.UsageError("Tests require a dedicated database ending in _test")
    from app.migrate import run_migrations

    run_migrations(dsn)
    return dsn


@pytest.fixture
def client(database_dsn):
    from app.main import create_app

    with psycopg.connect(database_dsn) as connection:
        connection.execute("TRUNCATE notes RESTART IDENTITY")
    with TestClient(create_app(database_dsn)) as client:
        yield client
