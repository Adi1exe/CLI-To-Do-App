"""
ORM Models — SQLAlchemy table definitions.
These map directly to SQLite tables on disk.
"""

from sqlalchemy import Column, Integer, String, Boolean, Date, Enum as SAEnum
from app.db_session import Base
from app.schemas import Priority


class Task(Base):
    __tablename__ = "tasks"

    id          = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title       = Column(String(100), nullable=False)
    description = Column(String(500), nullable=True)
    priority    = Column(SAEnum(Priority), default=Priority.medium, nullable=False)
    completed   = Column(Boolean, default=False, nullable=False)
    due_date    = Column(Date, nullable=True)