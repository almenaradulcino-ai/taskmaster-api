"""Acesso ao banco SQLite usado pela API."""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


DATABASE_PATH = Path(__file__).resolve().parent.parent / "taskmaster.db"


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    """Abre uma conexão e garante que ela seja fechada ao final."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def initialize_database() -> None:
    """Cria a tabela de tarefas se ela ainda não existir."""
    with connect() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                completed INTEGER NOT NULL DEFAULT 0
                    CHECK (completed IN (0, 1))
            )
            """
        )


def create_task(title: str, description: str) -> dict[str, object]:
    """Insere uma tarefa e devolve a linha criada."""
    with connect() as connection:
        cursor = connection.execute(
            "INSERT INTO tasks (title, description) VALUES (?, ?)",
            (title, description),
        )
        row = connection.execute(
            "SELECT id, title, description, completed FROM tasks WHERE id = ?",
            (cursor.lastrowid,),
        ).fetchone()
        return dict(row)


def list_tasks() -> list[dict[str, object]]:
    """Devolve todas as tarefas, da mais nova para a mais antiga."""
    with connect() as connection:
        rows = connection.execute(
            "SELECT id, title, description, completed FROM tasks ORDER BY id DESC"
        ).fetchall()
        return [dict(row) for row in rows]


def get_task(task_id: int) -> dict[str, object] | None:
    """Busca uma tarefa pelo ID ou devolve None se não existir."""
    with connect() as connection:
        row = connection.execute(
            "SELECT id, title, description, completed FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()
        return dict(row) if row is not None else None


def update_task(
    task_id: int,
    title: str,
    description: str,
    completed: bool,
) -> dict[str, object] | None:
    """Atualiza uma tarefa existente e devolve os dados atualizados."""
    with connect() as connection:
        cursor = connection.execute(
            """
            UPDATE tasks
            SET title = ?, description = ?, completed = ?
            WHERE id = ?
            """,
            (title, description, int(completed), task_id),
        )
        if cursor.rowcount == 0:
            return None

        row = connection.execute(
            "SELECT id, title, description, completed FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()
        return dict(row)


def delete_task(task_id: int) -> bool:
    """Remove uma tarefa pelo ID e informa se ela existia."""
    with connect() as connection:
        cursor = connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        return cursor.rowcount > 0
