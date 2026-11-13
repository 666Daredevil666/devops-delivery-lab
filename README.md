# DevOps Delivery Lab

FastAPI notes API backed by PostgreSQL 17. Python 3.13 and Docker Compose.

## Run

Requires Docker Engine with Compose v2.

```sh
cp .env.example .env
docker compose up --build -d --wait
python3 scripts/smoke.py
```

API: `http://127.0.0.1:8000`; OpenAPI: `/docs`.

| Route | Purpose |
| --- | --- |
| `GET /health/live` | Process liveness; independent of PostgreSQL |
| `GET /health/ready` | Database connectivity and schema readiness |
| `POST /notes` | Create a note: `{"title":"Release","content":"Deploy v1"}` |
| `GET /notes?limit=50&offset=0` | List notes; maximum 100 per request |
| `GET /notes/{id}` | Read one note |

Migrations run before the API starts. Database failures return `503`; note data lives in a named volume.
The API is bound to localhost. This stage has no authentication.

## Verify

```sh
docker compose --profile test run --build --rm tests
docker compose run --rm migrate
python3 scripts/smoke.py
```

Tests use a separate, ephemeral `notes_test` database. To check an outage, stop `db` and request both health endpoints: liveness stays `200`, readiness returns `503`. Start `db` to recover.

```sh
docker compose stop db
curl -i http://127.0.0.1:8000/health/live
curl -i http://127.0.0.1:8000/health/ready
docker compose start db
```

`docker compose down` retains data. `docker compose --profile test down -v` removes the lab's containers and database volume.
