from pathlib import Path

from app.db import connect

MIGRATIONS_DIR = Path(__file__).parent / "migrations"


def run_migrations(dsn: str = "") -> None:
    with connect(dsn) as connection:
        connection.execute("SELECT pg_advisory_xact_lock(942137)")
        connection.execute(
            "CREATE TABLE IF NOT EXISTS schema_migrations (version text PRIMARY KEY)"
        )
        for path in sorted(MIGRATIONS_DIR.glob("*.sql")):
            applied = connection.execute(
                "SELECT 1 FROM schema_migrations WHERE version = %s", (path.name,)
            ).fetchone()
            if applied is None:
                connection.execute(path.read_text(encoding="utf-8"))
                connection.execute(
                    "INSERT INTO schema_migrations (version) VALUES (%s)", (path.name,)
                )


if __name__ == "__main__":
    run_migrations()
    print("Database migrations complete")
