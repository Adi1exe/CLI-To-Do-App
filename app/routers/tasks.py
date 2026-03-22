"""
Router: /tasks
All task-related endpoints — CRUD + filtering + summary.
"""

from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from sqlalchemy.orm import Session

from app.schemas import TaskCreate, TaskUpdate, TaskResponse, SummaryResponse, Priority
from app.db_session import get_db
import app.database as db

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
)


# ─── SUMMARY ──────────────────────────────────────────────────────────────────

@router.get(
    "/summary",
    response_model=SummaryResponse,
    summary="Get task statistics dashboard",
)
def get_summary(session: Session = Depends(get_db)):
    """
    Returns a quick overview:
    - total / pending / completed task counts
    - overdue count (pending tasks past their due date)
    - high priority pending count
    """
    return db.get_summary(session)


# ─── CREATE ───────────────────────────────────────────────────────────────────

@router.post(
    "/",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
)
def create_task(payload: TaskCreate, session: Session = Depends(get_db)):
    """
    Create a to-do task.
    - **title**: required, 1–100 chars
    - **description**: optional
    - **priority**: `low` | `medium` (default) | `high`
    - **due_date**: optional, format `YYYY-MM-DD`
    """
    return db.create_task(session, payload)


# ─── READ (all) with filters ──────────────────────────────────────────────────

@router.get(
    "/",
    response_model=List[TaskResponse],
    summary="Fetch tasks (with optional filters)",
)
def get_all_tasks(
    priority:  Optional[Priority] = Query(None, description="Filter by priority"),
    completed: Optional[bool]     = Query(None, description="Filter by completion status"),
    search:    Optional[str]      = Query(None, description="Search in title or description"),
    page:      int                = Query(1,    ge=1,       description="Page number"),
    limit:     int                = Query(10,   ge=1, le=100, description="Results per page"),
    session:   Session            = Depends(get_db),
):
    """
    Fetch tasks with optional query params:

    | Param       | Example               |
    |-------------|-----------------------|
    | `priority`  | `?priority=high`      |
    | `completed` | `?completed=false`    |
    | `search`    | `?search=grocery`     |
    | `page`      | `?page=2&limit=5`     |
    """
    return db.get_all_tasks(session, priority=priority, completed=completed,
                            search=search, page=page, limit=limit)


# ─── READ (by ID) ─────────────────────────────────────────────────────────────

@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Fetch a single task by ID",
)
def get_task(task_id: int, session: Session = Depends(get_db)):
    task = db.get_task_by_id(session, task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Task with id={task_id} not found.")
    return task


# ─── UPDATE ───────────────────────────────────────────────────────────────────

@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Partially update a task",
)
def update_task(task_id: int, payload: TaskUpdate, session: Session = Depends(get_db)):
    """Update any subset of fields. Only provided fields are changed."""
    task = db.update_task(session, task_id, payload)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Task with id={task_id} not found.")
    return task


# ─── DELETE ───────────────────────────────────────────────────────────────────

@router.delete(
    "/{task_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a task",
)
def delete_task(task_id: int, session: Session = Depends(get_db)):
    success = db.delete_task(session, task_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Task with id={task_id} not found.")
    return {"message": f"Task {task_id} deleted successfully."}