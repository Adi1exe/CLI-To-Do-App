"""
Data Access Layer — all DB operations using SQLAlchemy ORM.
The router imports these functions; it never touches the ORM directly.
"""

from datetime import date
from typing import Optional
from sqlalchemy.orm import Session

from app.models import Task
from app.schemas import TaskCreate, TaskUpdate, TaskResponse, Priority


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _to_response(task: Task) -> TaskResponse:
    """Convert ORM Task → Pydantic TaskResponse, injecting is_overdue."""
    overdue = (
        bool(task.due_date)
        and not task.completed
        and task.due_date < date.today()
    )
    return TaskResponse(
        id=task.id,
        title=task.title,
        description=task.description,
        priority=task.priority,
        completed=task.completed,
        due_date=task.due_date,
        is_overdue=overdue,
    )


# ─── CRUD ─────────────────────────────────────────────────────────────────────

def get_all_tasks(
    db: Session,
    priority:  Optional[Priority] = None,
    completed: Optional[bool]     = None,
    search:    Optional[str]      = None,
    page:      int = 1,
    limit:     int = 10,
) -> list[TaskResponse]:
    query = db.query(Task)

    if priority is not None:
        query = query.filter(Task.priority == priority)
    if completed is not None:
        query = query.filter(Task.completed == completed)
    if search:
        like = f"%{search}%"
        query = query.filter(
            Task.title.ilike(like) | Task.description.ilike(like)
        )

    offset = (page - 1) * limit
    tasks  = query.offset(offset).limit(limit).all()
    return [_to_response(t) for t in tasks]


def get_task_by_id(db: Session, task_id: int) -> Optional[TaskResponse]:
    task = db.query(Task).filter(Task.id == task_id).first()
    return _to_response(task) if task else None


def create_task(db: Session, payload: TaskCreate) -> TaskResponse:
    task = Task(
        title=payload.title,
        description=payload.description,
        priority=payload.priority,
        completed=False,
        due_date=payload.due_date,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return _to_response(task)


def update_task(db: Session, task_id: int, payload: TaskUpdate) -> Optional[TaskResponse]:
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        return None

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return _to_response(task)


def delete_task(db: Session, task_id: int) -> bool:
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        return False
    db.delete(task)
    db.commit()
    return True


# ─── Summary ──────────────────────────────────────────────────────────────────

def get_summary(db: Session) -> dict:
    all_tasks = db.query(Task).all()
    total     = len(all_tasks)
    completed = sum(1 for t in all_tasks if t.completed)
    pending   = total - completed
    overdue   = sum(
        1 for t in all_tasks
        if t.due_date and not t.completed and t.due_date < date.today()
    )
    high_prio_pending = sum(
        1 for t in all_tasks
        if not t.completed and t.priority == Priority.high
    )
    return {
        "total":                 total,
        "pending":               pending,
        "completed":             completed,
        "overdue":               overdue,
        "high_priority_pending": high_prio_pending,
    }