from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel, Field

from app.database import (
    create_task as save_task,
    delete_task as remove_task,
    get_task as find_task,
    initialize_database,
    list_tasks as fetch_tasks,
    update_task as save_task_changes,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title="TaskMaster API",
    description="API para organizar tarefas pessoais.",
    version="0.1.0",
    lifespan=lifespan,
)


class TaskCreate(BaseModel):
    """Campos que o cliente precisa enviar para criar uma tarefa."""

    title: str = Field(min_length=1, max_length=100)
    description: str = Field(default="", max_length=500)


class TaskResponse(BaseModel):
    """Formato de tarefa que a API devolve ao cliente."""

    id: int
    title: str
    description: str
    completed: bool


class TaskUpdate(BaseModel):
    """Campos completos enviados para substituir os dados de uma tarefa."""

    title: str = Field(min_length=1, max_length=100)
    description: str = Field(max_length=500)
    completed: bool


@app.get("/health")
def health_check():
    """Confirma que a API está em execução."""
    return {"status": "ok"}


@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate):
    """Cria uma tarefa e a salva no banco SQLite."""
    return save_task(task.title, task.description)


@app.get("/tasks", response_model=list[TaskResponse])
def list_tasks():
    """Retorna todas as tarefas salvas no banco."""
    return fetch_tasks()


@app.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int):
    """Retorna uma tarefa específica ou informa que ela não existe."""
    task = find_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    return task


@app.put("/tasks/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task: TaskUpdate):
    """Substitui os dados editáveis de uma tarefa existente."""
    updated_task = save_task_changes(
        task_id=task_id,
        title=task.title,
        description=task.description,
        completed=task.completed,
    )
    if updated_task is None:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    return updated_task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    """Remove uma tarefa existente."""
    deleted = remove_task(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

