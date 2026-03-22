"""
App factory — registers routers, creates DB tables on startup.
"""

from fastapi import FastAPI
from app.db_session import engine, Base
from app.routers import tasks
import app.models  # noqa: F401 — ensures models are registered with Base


def create_app() -> FastAPI:
    # Create all SQLite tables if they don't exist yet
    Base.metadata.create_all(bind=engine)

    app = FastAPI(
        title="Console To-Do API",
        description="A modular FastAPI To-Do app with SQLite persistence, filters, and a summary dashboard.",
        version="2.0.0",
    )

    app.include_router(tasks.router)

    @app.get("/", tags=["Health"])
    def root():
        return {"status": "ok", "message": "To-Do API v2 is running 🚀"}

    return app