import psycopg
from psycopg.rows import dict_row


def connect(dsn: str = "") -> psycopg.Connection:
    return psycopg.connect(
        dsn,
        connect_timeout=2,
        options="-c statement_timeout=3000 -c lock_timeout=3000",
        row_factory=dict_row,
    )
