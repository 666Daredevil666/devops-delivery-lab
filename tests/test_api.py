from datetime import datetime

import psycopg
import pytest
from fastapi.testclient import TestClient

UNAVAILABLE_DATABASE = (
    "host=127.0.0.1 port=1 dbname=notes_test user=notes password=not-for-responses"
)


def test_liveness_does_not_require_database():
    from app.main import create_app

    with TestClient(create_app(UNAVAILABLE_DATABASE)) as client:
        response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.parametrize("path", ["/health/ready", "/notes", "/notes/1"])
def test_database_outage_returns_sanitized_503(path):
    from app.main import create_app

    with TestClient(create_app(UNAVAILABLE_DATABASE)) as client:
        response = client.get(path)
    assert response.status_code == 503
    assert response.json() == {"detail": "Database unavailable"}
    assert response.headers["retry-after"] == "3"
    assert "not-for-responses" not in response.text


def test_create_during_database_outage_returns_503():
    from app.main import create_app

    with TestClient(create_app(UNAVAILABLE_DATABASE)) as client:
        response = client.post("/notes", json={"title": "Release", "content": "Deploy v1"})
    assert response.status_code == 503


def test_readiness_checks_database(client):
    assert client.get("/health/ready").status_code == 200


def test_created_note_is_persisted_and_can_be_read(client, database_dsn):
    response = client.post("/notes", json={"title": " Release ", "content": "Deploy v1"})
    assert response.status_code == 201
    note = response.json()
    assert note["id"] == 1
    assert note["title"] == "Release"
    assert note["content"] == "Deploy v1"
    assert datetime.fromisoformat(note["created_at"]).tzinfo is not None
    assert response.headers["location"] == "/notes/1"
    assert client.get("/notes/1").json() == note
    assert client.get("/notes").json() == [note]
    with psycopg.connect(database_dsn) as connection:
        assert connection.execute("SELECT title, content FROM notes").fetchone() == (
            "Release",
            "Deploy v1",
        )


def test_note_content_is_not_interpreted_as_sql(client):
    content = "'); DROP TABLE notes; -- Привет"
    response = client.post("/notes", json={"title": "SQL text", "content": content})
    assert response.status_code == 201
    assert client.get("/notes/1").json()["content"] == content
    assert len(client.get("/notes").json()) == 1


def test_missing_note_returns_404(client):
    assert client.get("/notes/999").status_code == 404


@pytest.mark.parametrize(
    "payload",
    [
        {"title": " ", "content": "text"},
        {"title": "x" * 121, "content": "text"},
        {"title": "title", "content": " "},
        {"title": "title", "content": "x" * 10001},
        {"title": "bad\u0000title", "content": "text"},
        {"title": "title", "content": "bad\u0000content"},
        {"title": "title"},
    ],
)
def test_invalid_notes_are_rejected_without_writing(client, payload):
    assert client.post("/notes", json=payload).status_code == 422
    assert client.get("/notes").json() == []


def test_list_is_bounded_and_ordered(client):
    for title in ["first", "second", "third"]:
        assert client.post("/notes", json={"title": title, "content": "body"}).status_code == 201
    response = client.get("/notes?limit=1&offset=1")
    assert response.status_code == 200
    assert [note["title"] for note in response.json()] == ["second"]
    for query in ["limit=0", "limit=101", "offset=-1"]:
        assert client.get(f"/notes?{query}").status_code == 422
