"""
Entry point — run with:  python run.py
or directly:             uvicorn app.main:app --reload
"""

import uvicorn
from app.main import create_app

app = create_app()

if __name__ == "__main__":
    uvicorn.run("run:app", host="127.0.0.1", port=8000, reload=True)
