"""
In-memory "database" for the To-Do app.
Acts as the data-access layer — all DB logic lives here,
keeping the router clean and swap-friendly (replace with SQLAlchemy later if needed).
"""

from typing import Dict, Optional
from app.schemas import TaskCreate, TaskUpdate, TaskResponse

# Simple dict acting as our in-memory store  { id: TaskResponse }
_db: Dict[int, TaskResponse] = {}
_id_counter: int = 1  # Auto-increment PK


def get_all_tasks() -> list[TaskResponse]:
    return list(_db.values())


def get_task_by_id(task_id: int) -> Optional[TaskResponse]:
    return _db.get(task_id)


def create_task(payload: TaskCreate) -> TaskResponse:
    global _id_counter
    task = TaskResponse(
        id=_id_counter,
        title=payload.title,
        description=payload.description,
        priority=payload.priority,
        completed=False,
    )
    _db[_id_counter] = task
    _id_counter += 1
    return task


def update_task(task_id: int, payload: TaskUpdate) -> Optional[TaskResponse]:
    task = _db.get(task_id)
    if not task:
        return None

    updated_data = task.model_dump()
    patch = payload.model_dump(exclude_unset=True)   # only supplied fields
    updated_data.update(patch)

    updated_task = TaskResponse(**updated_data)
    _db[task_id] = updated_task
    return updated_task


def delete_task(task_id: int) -> bool:
    if task_id not in _db:
        return False
    del _db[task_id]
    return True
