from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class TaskCreate(BaseModel):
    """Schema for creating a new task."""
    title: str = Field(..., min_length=1, max_length=100, description="Title of the task")
    description: Optional[str] = Field(None, max_length=500, description="Optional task description")
    priority: Priority = Field(Priority.medium, description="Task priority: low | medium | high")

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "priority": "medium"
            }
        }
    }

class TaskUpdate(BaseModel):
    """Schema for updating an existing task (all fields optional)."""
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    priority: Optional[Priority] = None
    completed: Optional[bool] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Buy groceries (updated)",
                "completed": True
            }
        }
    }

class TaskResponse(BaseModel):
    """Schema for task responses sent back to the client."""
    id: int
    title: str
    description: Optional[str]
    priority: Priority
    completed: bool

    model_config = {"from_attributes": True}