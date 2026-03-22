"""
Pydantic Schemas — request/response validation via Pydantic v2.
"""

from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import date


class Priority(str, Enum):
    low    = "low"
    medium = "medium"
    high   = "high"


# ─── Request schemas ──────────────────────────────────────────────────────────

class TaskCreate(BaseModel):
    """Schema for creating a new task."""
    title:       str            = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    priority:    Priority       = Field(Priority.medium)
    due_date:    Optional[date] = Field(None, description="Due date in YYYY-MM-DD format")

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "priority": "medium",
                "due_date": "2025-12-31"
            }
        }
    }


class TaskUpdate(BaseModel):
    """Schema for partially updating a task (all fields optional)."""
    title:       Optional[str]      = Field(None, min_length=1, max_length=100)
    description: Optional[str]      = Field(None, max_length=500)
    priority:    Optional[Priority] = None
    completed:   Optional[bool]     = None
    due_date:    Optional[date]     = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "completed": True,
                "due_date": "2025-11-01"
            }
        }
    }


# ─── Response schemas ─────────────────────────────────────────────────────────

class TaskResponse(BaseModel):
    """What the API sends back to the client."""
    id:          int
    title:       str
    description: Optional[str]
    priority:    Priority
    completed:   bool
    due_date:    Optional[date]
    is_overdue:  bool = False   # computed — not stored in DB

    model_config = {"from_attributes": True}


class SummaryResponse(BaseModel):
    total:                 int
    pending:               int
    completed:             int
    overdue:               int
    high_priority_pending: int