from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel, field_validator
from typing import Optional

from database import get_db, init_db

app = FastAPI(
    title="Task API",
    version="3.0",
    description="CRUD API for managing a to-do list — backed by PostgreSQL in Docker",
)

# ── Initialise DB on startup ──────────────────────────────────────────────────
init_db()


# ── Pydantic models ───────────────────────────────────────────────────────────

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


# ── 422 → 400 ─────────────────────────────────────────────────────────────────

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"error": "Bad request — missing or invalid fields"},
    )


# ── Root & Health ─────────────────────────────────────────────────────────────

@app.get("/", summary="API info")
def root():
    return {"name": "Task API", "version": "3.0", "endpoints": ["/tasks"]}


@app.get("/health", summary="Health check")
def health():
    """Pings the database with SELECT 1 to confirm connectivity."""
    try:
        with get_db() as conn:
            conn.execute("SELECT 1")
        db_status = "ok"
    except Exception as e:
        db_status = f"error: {e}"
    return {"status": "ok", "db": db_status}


# ── Stage 2: Read endpoints ───────────────────────────────────────────────────

@app.get("/tasks", summary="List all tasks",
         description="Returns every task. Optional: ?search=<text>, ?done=true|false.")
def get_tasks(search: Optional[str] = None, done: Optional[bool] = None):
    query = "SELECT * FROM tasks WHERE TRUE"
    params: list = []

    if search is not None:
        query += " AND title ILIKE %s"
        params.append(f"%{search}%")

    if done is not None:
        query += " AND done = %s"
        params.append(done)

    with get_db() as conn:
        rows = conn.execute(query, params).fetchall()
    return rows


@app.get("/tasks/{task_id}", summary="Get one task by ID")
def get_task(task_id: int):
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM tasks WHERE id = %s", (task_id,)
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return row


# ── Stage 3: Create ───────────────────────────────────────────────────────────

@app.post("/tasks", status_code=201, summary="Create a new task")
def create_task(task: TaskCreate):
    with get_db() as conn:
        row = conn.execute(
            "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING *",
            (task.title.strip(), False),
        ).fetchone()
        conn.commit()
    return row


# ── Stage 3: Update ───────────────────────────────────────────────────────────

@app.put("/tasks/{task_id}", summary="Update an existing task")
def update_task(task_id: int, task_update: TaskUpdate):
    with get_db() as conn:
        current = conn.execute(
            "SELECT * FROM tasks WHERE id = %s", (task_id,)
        ).fetchone()
        if current is None:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

        new_title = task_update.title.strip() if task_update.title is not None else current["title"]
        new_done  = task_update.done          if task_update.done  is not None else current["done"]

        row = conn.execute(
            "UPDATE tasks SET title = %s, done = %s WHERE id = %s RETURNING *",
            (new_title, new_done, task_id),
        ).fetchone()
        conn.commit()
    return row


# ── Stage 3: Delete ───────────────────────────────────────────────────────────

@app.delete("/tasks/{task_id}", status_code=204, summary="Delete a task")
def delete_task(task_id: int):
    with get_db() as conn:
        row = conn.execute(
            "SELECT id FROM tasks WHERE id = %s", (task_id,)
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
        conn.execute("DELETE FROM tasks WHERE id = %s", (task_id,))
        conn.commit()
    # 204 No Content
