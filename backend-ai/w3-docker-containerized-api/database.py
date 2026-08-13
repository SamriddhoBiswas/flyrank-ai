import os
import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.environ["DATABASE_URL"]


def get_db():
    """Open a psycopg connection with dict_row so rows come back as dicts."""
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)


def init_db():
    """
    Create the tasks table if it doesn't exist, then seed three example
    tasks — only when the table is currently empty (first-run rule).
    """
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id    SERIAL PRIMARY KEY,
                title TEXT    NOT NULL,
                done  BOOLEAN NOT NULL DEFAULT FALSE
            )
        """)

        count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()["count"]
        if count == 0:
            seed = [
                ("Learn HTTP basics",         False),
                ("Build a CRUD API",           False),
                ("Test everything in Swagger", False),
            ]
            conn.executemany(
                "INSERT INTO tasks (title, done) VALUES (%s, %s)",
                seed
            )
        conn.commit()
