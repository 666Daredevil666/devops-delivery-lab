import logging
from datetime import datetime
from typing import Annotated

import psycopg
from fastapi import FastAPI, HTTPException, Path, Query, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, StringConstraints, field_validator

from app.db import connect

logger = logging.getLogger(__name__)


class NoteCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]
    content: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=10000)
    ]

    @field_validator("title", "content")
    @classmethod
    def reject_null_characters(cls, value: str) -> str:
        if "\x00" in value:
            raise ValueError("NUL characters are not supported")
        return value


class Note(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime


def create_app(database_dsn: str = "") -> FastAPI:
    application = FastAPI(title="DevOps Delivery Lab", version="0.1.0")

    @application.exception_handler(psycopg.Error)
    async def database_error(request: Request, exc: psycopg.Error) -> JSONResponse:
        logger.warning("Database request failed: %s", type(exc).__name__)
        return JSONResponse(
            status_code=503,
            content={"detail": "Database unavailable"},
            headers={"Retry-After": "3"},
        )

    @application.get("/health/live")
    def live() -> dict[str, str]:
        return {"status": "ok"}

    @application.get("/health/ready")
    def ready() -> dict[str, str]:
        with connect(database_dsn) as connection:
            connection.execute("SELECT id FROM notes LIMIT 0")
        return {"status": "ok"}

    @application.post("/notes", response_model=Note, status_code=201)
    def create_note(note: NoteCreate, response: Response):
        with connect(database_dsn) as connection:
            row = connection.execute(
                "INSERT INTO notes (title, content) VALUES (%s, %s) "
                "RETURNING id, title, content, created_at",
                (note.title, note.content),
            ).fetchone()
        response.headers["Location"] = f"/notes/{row['id']}"
        return row

    @application.get("/notes", response_model=list[Note])
    def list_notes(
        limit: Annotated[int, Query(ge=1, le=100)] = 50,
        offset: Annotated[int, Query(ge=0)] = 0,
    ):
        with connect(database_dsn) as connection:
            return connection.execute(
                "SELECT id, title, content, created_at FROM notes ORDER BY id LIMIT %s OFFSET %s",
                (limit, offset),
            ).fetchall()

    @application.get("/notes/{note_id}", response_model=Note)
    def read_note(note_id: Annotated[int, Path(gt=0)]):
        with connect(database_dsn) as connection:
            row = connection.execute(
                "SELECT id, title, content, created_at FROM notes WHERE id = %s", (note_id,)
            ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Note not found")
        return row

    return application


app = create_app()
