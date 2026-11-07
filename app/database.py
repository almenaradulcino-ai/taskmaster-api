"""Acesso ao banco SQLite usado pela API."""

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator


DATABASE_URL = os.getenv("DATABASE_URL")
DEFAULT_DATABASE_PATH = Path(__file__).resolve().parent.parent / "taskmaster.db"
DATABASE_PATH = Path(os.getenv("TASKMASTER_DB_PATH", str(DEFAULT_DATABASE_PATH)))


def _open_connection() -> tuple[Any, bool]:
    """Abre PostgreSQL quando DATABASE_URL existe; caso contrário, usa SQLite."""
    if DATABASE_URL:
        import psycopg
        from psycopg.rows import dict_row

        return psycopg.connect(DATABASE_URL, row_factory=dict_row), True

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection, False


def _execute(
    connection: Any,
    statement: str,
    parameters: tuple[object, ...] = (),
) -> Any:
    """Executa SQL com o marcador de parâmetros esperado pelo driver ativo."""
    if DATABASE_URL:
        statement = statement.replace("?", "%s")
    return connection.execute(statement, parameters)


@contextmanager
def connect() -> Iterator[Any]:
    """Abre uma conexão e garante que ela seja fechada ao final."""
    connection, _ = _open_connection()
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def initialize_database() -> None:
    """Cria a tabela no PostgreSQL ou SQLite, conforme a configuração."""
    if DATABASE_URL:
        id_column = "SERIAL PRIMARY KEY"
        completed_column = "BOOLEAN NOT NULL DEFAULT FALSE"
    else:
        id_column = "INTEGER PRIMARY KEY AUTOINCREMENT"
        completed_column = "INTEGER NOT NULL DEFAULT 0 CHECK (completed IN (0, 1))"

    with connect() as connection:
        connection.execute(
            f"""
            CREATE TABLE IF NOT EXISTS tasks (
                id {id_column},
                title TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                completed {completed_column}
            )
            """
        )


def create_task(
    title: str,
    description: str,
    completed: bool = False,
) -> dict[str, object]:
    """Insere uma tarefa e devolve a linha criada."""
    with connect() as connection:
        row = _execute(
            connection,
            """
            INSERT INTO tasks (title, description, completed)
            VALUES (?, ?, ?)
            RETURNING id, title, description, completed
            """,
            (title, description, completed),
        ).fetchone()
        return dict(row)


def list_tasks() -> list[dict[str, object]]:
    """Devolve todas as tarefas, da mais nova para a mais antiga."""
    with connect() as connection:
        rows = _execute(
            connection,
            "SELECT id, title, description, completed FROM tasks ORDER BY id DESC"
        ).fetchall()
        return [dict(row) for row in rows]


def get_task(task_id: int) -> dict[str, object] | None:
    """Busca uma tarefa pelo ID ou devolve None se não existir."""
    with connect() as connection:
        row = _execute(
            connection,
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
        cursor = _execute(
            connection,
            """
            UPDATE tasks
            SET title = ?, description = ?, completed = ?
            WHERE id = ?
            """,
            (title, description, completed, task_id),
        )
        if cursor.rowcount == 0:
            return None

        row = _execute(
            connection,
            "SELECT id, title, description, completed FROM tasks WHERE id = ?",
            (task_id,),
        ).fetchone()
        return dict(row)


def delete_task(task_id: int) -> bool:
    """Remove uma tarefa pelo ID e informa se ela existia."""
    with connect() as connection:
        cursor = _execute(connection, "DELETE FROM tasks WHERE id = ?", (task_id,))
        return cursor.rowcount > 0
