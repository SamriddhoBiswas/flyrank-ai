import sqlite3
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, field_validator
from typing import Optional

app = FastAPI(title="Task API", version="2.0",
              description="A CRUD API for managing a to-do list — backed by SQLite (tasks.db)")

# ── Database helpers ─────────────────────────────────────────────────────────

DB_PATH = "tasks.db"


def get_db():
    """Open a database connection with row_factory so rows behave like dicts."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row   # lets us do row["id"], row["title"], etc.
    return conn


def row_to_dict(row: sqlite3.Row) -> dict:
    """Convert a sqlite3.Row to a plain dict, casting done to bool."""
    return {
        "id": row["id"],
        "title": row["title"],
        "done": bool(row["done"]),
    }


# ── Stage 0: Initialise the database on startup ──────────────────────────────

def init_db():
    """
    Create the tasks table if it doesn't exist, then seed three example
    tasks — but ONLY when the table is currently empty.
    """
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id    INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT    NOT NULL,
                done  INTEGER NOT NULL DEFAULT 0
            )
        """)
        conn.commit()

        # Seed only on first run (count = 0)
        count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        if count == 0:
            seed_tasks = [
                ("Learn HTTP basics",        0),
                ("Build a CRUD API",          0),
                ("Test everything in Swagger", 0),
            ]
            conn.executemany(
                "INSERT INTO tasks (title, done) VALUES (?, ?)",
                seed_tasks
            )
            conn.commit()


# Run once at import / startup
init_db()


# ── Pydantic models for input validation ─────────────────────────────────────

class TaskCreate(BaseModel):
    title: str

    @field_validator("title")
    @classmethod
    def title_must_be_non_empty(cls, v):
        if not v or not v.strip():
            raise ValueError("Title is required and must be non-empty")
        return v


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done:  Optional[bool] = None

    @field_validator("title")
    @classmethod
    def title_must_be_non_empty(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Title must be non-empty")
        return v


# ── Convert FastAPI's default 422 → 400 (assignment requires 400) ─────────────

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"error": "Bad request — missing or invalid fields"}
    )


# ── Root & Health ─────────────────────────────────────────────────────────────

@app.get("/", summary="API info",
         description="Returns metadata about this API.")
def root():
    """Describes the API — name, version, available endpoints."""
    return {"name": "Task API", "version": "2.0", "endpoints": ["/tasks"]}


@app.get("/health", summary="Health check",
         description="Used by monitoring tools to check the server is alive.")
def health():
    """Returns ok if the server is running."""
    return {"status": "ok"}


# ── Stage 1: Read endpoints ───────────────────────────────────────────────────

@app.get("/tasks", summary="List all tasks",
         description="Returns every task in the to-do list. "
                     "Optional query params: ?search=<text>, ?done=true|false.")
def get_tasks(search: Optional[str] = None, done: Optional[bool] = None):
    """
    SELECT * FROM tasks — with optional LIKE search and/or done filter.
    Bonus extras: search and filter-by-status.
    """
    query = "SELECT * FROM tasks WHERE 1=1"
    params: list = []

    if search is not None:
        query += " AND title LIKE ?"
        params.append(f"%{search}%")

    if done is not None:
        query += " AND done = ?"
        params.append(1 if done else 0)

    with get_db() as conn:
        rows = conn.execute(query, params).fetchall()
    return [row_to_dict(r) for r in rows]


@app.get("/tasks/{task_id}", summary="Get one task by ID",
         description="Returns a single task. 404 if the ID doesn't exist.")
def get_task(task_id: int):
    """SELECT * FROM tasks WHERE id = ? — parameterized for safety."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()

    if row is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return row_to_dict(row)


# ── Stage 2: Create endpoint ──────────────────────────────────────────────────

@app.post("/tasks", status_code=201, summary="Create a new task",
          description="Adds a task to the list. Title is required; done defaults to false.")
def create_task(task: TaskCreate):
    """INSERT INTO tasks — database assigns the id via AUTOINCREMENT."""
    with get_db() as conn:
        cursor = conn.execute(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            (task.title.strip(), 0)
        )
        conn.commit()
        new_id = cursor.lastrowid

    return {"id": new_id, "title": task.title.strip(), "done": False}


# ── Stage 3: Update endpoint ──────────────────────────────────────────────────

@app.put("/tasks/{task_id}", summary="Update an existing task",
         description="Replaces title and/or done. 404 if ID unknown, 400 if title is empty.")
def update_task(task_id: int, task_update: TaskUpdate):
    """UPDATE tasks SET … WHERE id = ? — parameterized for safety."""
    with get_db() as conn:
        # First confirm the task exists
        row = conn.execute(
            "SELECT * FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

        current = row_to_dict(row)

        new_title = task_update.title.strip() if task_update.title is not None else current["title"]
        new_done  = task_update.done          if task_update.done  is not None else current["done"]

        conn.execute(
            "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
            (new_title, 1 if new_done else 0, task_id)
        )
        conn.commit()

    return {"id": task_id, "title": new_title, "done": new_done}


# ── Stage 3: Delete endpoint ──────────────────────────────────────────────────

@app.delete("/tasks/{task_id}", status_code=204, summary="Delete a task",
            description="Removes a task. Returns 204 (no content) on success, 404 if unknown.")
def delete_task(task_id: int):
    """DELETE FROM tasks WHERE id = ? — parameterized for safety."""
    with get_db() as conn:
        row = conn.execute(
            "SELECT id FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
    # 204 No Content — empty body