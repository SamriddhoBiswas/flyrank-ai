# W3: Containerize the stack

A CRUD API for managing a to-do list — built with **FastAPI**, backed by **PostgreSQL** running in **Docker**.  
Start the entire stack (app + database) with **one command**.

---

## Quick start

```bash
# 1. Copy the env template
cp .env.example .env          # Windows: copy .env.example .env

# 2. Start everything
docker compose up
```

The API is live at <http://localhost:8000>  
Swagger UI: <http://localhost:8000/docs>

> Data persists across restarts thanks to the `taskdata` Docker volume.  
> To reset: `docker compose down -v` (drops the volume too).

---

## Why PostgreSQL + Docker?

| Question | Answer |
|---|---|
| Why Postgres? | A full database server — the same engine behind FlyRank and most real backends. Handles concurrent writes, transactions, and scales to production. |
| Why Docker? | No local Postgres install needed. The exact same container runs on every machine, eliminating "works on my machine" bugs. |
| Why a volume? | Data lives outside the container. `docker compose down && docker compose up` brings the database back with all rows intact. |

---

## Environment variables

Copy `.env.example` to `.env` and set the values:

| Variable | Example | Description |
|---|---|---|
| `DATABASE_URL` | `postgres://postgres:dev@localhost:5432/tasks` | Postgres connection string |

> **Never commit `.env`** — it's git-ignored. `.env.example` is the safe committed placeholder.

---

## Endpoints

| Method   | Path            | Description                          | Success | Errors   |
|----------|-----------------|--------------------------------------|---------|----------|
| `GET`    | `/`             | API info                             | 200     | —        |
| `GET`    | `/health`       | Health check (pings the DB)          | 200     | —        |
| `GET`    | `/tasks`        | List all tasks (+ optional filters)  | 200     | —        |
| `GET`    | `/tasks/{id}`   | Get one task                         | 200     | 404      |
| `POST`   | `/tasks`        | Create a task                        | 201     | 400      |
| `PUT`    | `/tasks/{id}`   | Update a task                        | 200     | 400, 404 |
| `DELETE` | `/tasks/{id}`   | Delete a task                        | 204     | 404      |

### Optional query params for `GET /tasks`

| Param    | Example                        | What it does                        |
|----------|--------------------------------|-------------------------------------|
| `search` | `GET /tasks?search=milk`       | Case-insensitive title filter (ILIKE) |
| `done`   | `GET /tasks?done=true`         | Filter by completion status         |

---

## Example curl session

```bash
# Create a task
curl -i -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Buy milk"}'
# HTTP/1.1 201 Created
# {"id":4,"title":"Buy milk","done":false}

# List all tasks
curl -i http://localhost:8000/tasks

# Mark task 4 done
curl -i -X PUT http://localhost:8000/tasks/4 \
  -H "Content-Type: application/json" \
  -d '{"done":true}'

# Delete task 4
curl -i -X DELETE http://localhost:8000/tasks/4
# HTTP/1.1 204 No Content

# Unknown ID → 404
curl -i http://localhost:8000/tasks/999
# HTTP/1.1 404 Not Found
# {"detail":"Task 999 not found"}
```

---

## Project structure

```
.
├── main.py          # FastAPI routes — no DB code here
├── database.py      # All Postgres logic (connection, init, seed)
├── Dockerfile       # Builds the API image
├── compose.yaml     # Defines api + db services
├── requirements.txt
├── .env.example     # Committed placeholder — copy to .env
└── .env             # Real secrets — git-ignored
```

---

## Storage history

| Assignment | Storage | Engine |
|---|---|---|
| A1 | In-memory list | Python variable |
| A2 | `tasks.db` file | SQLite |
| **A3 (this)** | **Postgres rows** | **Docker container** |

Same five API endpoints the whole way. Storage is an implementation detail — the routes never changed.

---

## Notes

- `tasks.db` is **not** used here — Postgres replaces SQLite entirely.
- All SQL uses `%s` parameterized placeholders (psycopg3) — no user input is ever glued into SQL strings.
- Three seed tasks are inserted only on the very first run (table empty check).
- `GET /health` runs `SELECT 1` against the database — a real liveness check.
