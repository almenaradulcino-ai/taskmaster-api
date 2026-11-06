"""Testes automatizados das operações da API e do banco SQLite."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi import HTTPException
from pydantic import ValidationError

from app import database
from app.main import (
    TaskCreate,
    TaskUpdate,
    create_task,
    delete_task,
    get_task,
    health_check,
    list_tasks,
    update_task,
)


class TaskApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_directory = TemporaryDirectory()
        self.original_database_path = database.DATABASE_PATH
        database.DATABASE_PATH = Path(self.temp_directory.name) / "test_tasks.db"
        database.initialize_database()

    def tearDown(self) -> None:
        database.DATABASE_PATH = self.original_database_path
        self.temp_directory.cleanup()

    def test_health_check_returns_ok(self) -> None:
        self.assertEqual(health_check(), {"status": "ok"})

    def test_create_list_and_get_task(self) -> None:
        created = create_task(TaskCreate(title="Estudar Python"))

        self.assertEqual(created["title"], "Estudar Python")
        self.assertEqual(created["completed"], 0)
        self.assertEqual(list_tasks()[0]["id"], created["id"])
        self.assertEqual(get_task(created["id"])["title"], "Estudar Python")

    def test_input_validation_rejects_invalid_titles(self) -> None:
        with self.assertRaises(ValidationError):
            TaskCreate(title="")

        with self.assertRaises(ValidationError):
            TaskUpdate(title="x" * 101, description="", completed=False)

    def test_update_task_persists_changes(self) -> None:
        created = create_task(TaskCreate(title="Título antigo"))

        updated = update_task(
            created["id"],
            TaskUpdate(
                title="Título novo",
                description="Descrição atualizada",
                completed=True,
            ),
        )

        self.assertEqual(updated["title"], "Título novo")
        self.assertTrue(get_task(created["id"])["completed"])

    def test_delete_task_and_not_found_response(self) -> None:
        created = create_task(TaskCreate(title="Apagar depois"))

        response = delete_task(created["id"])

        self.assertEqual(response.status_code, 204)
        with self.assertRaises(HTTPException) as error:
            get_task(created["id"])
        self.assertEqual(error.exception.status_code, 404)


if __name__ == "__main__":
    unittest.main()
