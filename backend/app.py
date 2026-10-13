"""Existing task operations. Task creation is the workshop exercise."""
import os
import sqlite3
from contextlib import asynccontextmanager, contextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, StrictBool


class Task(BaseModel):
    id: int
    title: str
    description: str
    completed: bool


class TaskUpdate(BaseModel):
    completed: StrictBool


def create_app(db_path: str | Path | None = None) -> FastAPI:
    database = Path(db_path or os.environ.get("TASKS_DB", Path(__file__).with_name("tasks.sqlite3")))

    @contextmanager
    def connect():
        connection = sqlite3.connect(database)
        connection.row_factory = sqlite3.Row
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    @asynccontextmanager
    async def lifespan(app):
        database.parent.mkdir(parents=True, exist_ok=True)
        with connect() as connection:
            # Seed only when creating the table, never when users delete all tasks.
            exists = connection.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'").fetchone()
            connection.execute("CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, description TEXT NOT NULL DEFAULT '', completed INTEGER NOT NULL DEFAULT 0)")
            if not exists:
                connection.executemany("INSERT INTO tasks (title, description, completed) VALUES (?, ?, ?)", [
                    ("Read the API contract", "Agree on the frontend and backend boundary.", 0),
                    ("Create two worktrees", "Give each coding agent its own branch and directory.", 0),
                    ("Install the starter", "Check the existing application before making changes.", 1),
                ])
        yield

    app = FastAPI(title="Workshop Tasks", lifespan=lifespan)

    @app.get("/api/tasks", response_model=list[Task])
    def list_tasks():
        with connect() as connection:
            return [dict(row) for row in connection.execute("SELECT * FROM tasks ORDER BY id")]

    @app.patch("/api/tasks/{task_id}", response_model=Task)
    def update_task(task_id: int, update: TaskUpdate):
        with connect() as connection:
            result = connection.execute("UPDATE tasks SET completed = ? WHERE id = ?", (update.completed, task_id))
            if result.rowcount == 0:
                raise HTTPException(404, "Task not found")
            return dict(connection.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone())

    @app.delete("/api/tasks/{task_id}", status_code=204)
    def delete_task(task_id: int):
        with connect() as connection:
            result = connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            if result.rowcount == 0:
                raise HTTPException(404, "Task not found")
        return Response(status_code=204)

    return app


app = create_app()
