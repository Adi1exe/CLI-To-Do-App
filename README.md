# 📝 Console To-Do App — FastAPI + Pydantic

A fully modular, console-based CRUD To-Do application built with **FastAPI**, **Pydantic v2**, and an interactive Python CLI client.

---

## 📁 Project Structure

```
todo_app/
│
├── run.py                  # Uvicorn entry point
├── client.py               # Interactive console client
├── requirements.txt
│
└── app/
    ├── __init__.py
    ├── main.py             # App factory — registers routers
    ├── schemas.py          # Pydantic models (TaskCreate, TaskUpdate, TaskResponse)
    ├── database.py         # In-memory data access layer
    │
    └── routers/
        ├── __init__.py
        └── tasks.py        # All /tasks CRUD endpoints
```

---

## ⚙️ Setup

```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt
```

---

## 🚀 Running the App

### Step 1 — Start the API server
```bash
python run.py
```
The server starts at: `http://127.0.0.1:8000`  
Interactive docs (Swagger UI): `http://127.0.0.1:8000/docs`

### Step 2 — Run the console client (in a new terminal)
```bash
python client.py
```

---

## 🛠️ API Endpoints

| Method   | Endpoint         | Description              |
|----------|------------------|--------------------------|
| `POST`   | `/tasks/`        | Create a new task        |
| `GET`    | `/tasks/`        | Fetch all tasks          |
| `GET`    | `/tasks/{id}`    | Fetch a single task      |
| `PATCH`  | `/tasks/{id}`    | Partially update a task  |
| `DELETE` | `/tasks/{id}`    | Delete a task            |

---

## 📦 Schemas (Pydantic)

### TaskCreate (POST body)
```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "priority": "high"
}
```

### TaskUpdate (PATCH body — all fields optional)
```json
{
  "title": "Updated title",
  "completed": true
}
```

### TaskResponse
```json
{
  "id": 1,
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "priority": "high",
  "completed": false
}
```

---

## 💡 Notes

- **In-memory storage** — data resets when the server restarts. To persist data, swap `database.py` with a SQLAlchemy/SQLite implementation.
- **Priority levels**: `low`, `medium` (default), `high`
- Pydantic v2 is used for full request validation with descriptive error messages.
