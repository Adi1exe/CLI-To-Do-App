"""
Router: /tasks
All task-related endpoints live here.
"""

from fastapi import APIRouter, HTTPException, status
from typing import List

from app.schemas import TaskCreate, TaskUpdate, TaskResponse
import app.database as db

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
)


# ─── CREATE ───────────────────────────────────────────────────────────────────

@router.post(
    "/",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
)
def create_task(payload: TaskCreate):
    """
    Create a brand-new to-do task.

    - **title**: required, 1–100 chars
    - **description**: optional, up to 500 chars
    - **priority**: `low` | `medium` (default) | `high`
    """
    return db.create_task(payload)


# ─── READ (all) ───────────────────────────────────────────────────────────────

@router.get(
    "/",
    response_model=List[TaskResponse],
    summary="Fetch all tasks",
)
def get_all_tasks():
    """Return every task currently in the store."""
    return db.get_all_tasks()


# ─── READ (by ID) ─────────────────────────────────────────────────────────────

@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Fetch a single task by ID",
)
def get_task(task_id: int):
    """
    Retrieve one task by its numeric **task_id**.
    Returns 404 if no task with that ID exists.
    """
    task = db.get_task_by_id(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id={task_id} not found.",
        )
    return task


# ─── UPDATE ───────────────────────────────────────────────────────────────────

@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Partially update a task",
)
def update_task(task_id: int, payload: TaskUpdate):
    """
    Update **any subset** of a task's fields.
    Only the fields you include in the request body are changed.
    """
    task = db.update_task(task_id, payload)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id={task_id} not found.",
        )
    return task


# ─── DELETE ───────────────────────────────────────────────────────────────────

@router.delete(
    "/{task_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a task",
)
def delete_task(task_id: int):
    """
    Permanently remove a task by its **task_id**.
    Returns 404 if no task with that ID exists.
    """
    success = db.delete_task(task_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task with id={task_id} not found.",
        )
    return {"message": f"Task {task_id} deleted successfully."}
