"""
App factory — registers routers and configures the FastAPI instance.
"""

from fastapi import FastAPI
from app.routers import tasks

def create_app() -> FastAPI:
    app = FastAPI(
        title="Console To-Do API",
        description="A modular FastAPI-powered To-Do list with full CRUD support.",
        version="1.0.0",
    )

    # Register routers
    app.include_router(tasks.router)

    @app.get("/", tags=["Health"])
    def root():
        return {"status": "ok", "message": "To-Do API is running 🚀"}

    return app
