# 📝 Console To-Do App — v2

A modular, console-based CRUD To-Do application built with **FastAPI**, **SQLAlchemy (SQLite)**, and **Pydantic v2**. Fully persistent, filterable, and equipped with a live dashboard.

---

## 📁 Project Structure

```
todo_app/
│
├── run.py                      # Uvicorn server entry point
├── client.py                   # Interactive console client (CLI)
├── requirements.txt
├── todo.db                     # SQLite database (auto-created on first run)
│
└── app/
    ├── __init__.py
    ├── main.py                 # App factory — creates DB tables, registers routers
    ├── db_session.py           # SQLAlchemy engine, SessionLocal, get_db() dependency
    ├── models.py               # ORM table definition (Task)
    ├── schemas.py              # Pydantic v2 models for validation
    ├── database.py             # Data access layer — all DB queries live here
    │
    └── routers/
        ├── __init__.py
        └── tasks.py            # All /tasks endpoints (CRUD + filters + summary)
```

> Each layer has a single responsibility. The router calls the database layer, the database layer uses ORM models, and Pydantic schemas handle all validation independently.

---

## ⚙️ Setup & Installation

**Step 1 — Clone or download the project**

**Step 2 — Create and activate a virtual environment**

```bash
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

**Step 3 — Install dependencies**

```bash
pip install -r requirements.txt
```

**Dependencies installed:**

| Package | Purpose |
|---|---|
| `fastapi` | Web framework for building the API |
| `uvicorn[standard]` | ASGI server to run FastAPI |
| `sqlalchemy` | ORM for SQLite persistence |
| `pydantic` | Request/response validation |
| `requests` | HTTP client used by the console client |

---

## 🚀 Running the App

The app has two parts that run simultaneously in **two separate terminals**.

### Terminal 1 — Start the API server

```bash
python run.py
```

The server starts at `http://127.0.0.1:8000`.
The `todo.db` SQLite file is created automatically on first run.

### Terminal 2 — Start the console client

```bash
python client.py
```

The client connects to the running server and presents an interactive menu.

> 💡 **Swagger UI** is also available at `http://127.0.0.1:8000/docs` for testing endpoints directly in the browser.

---

## 🛠️ API Reference

### Base URL: `http://127.0.0.1:8000`

| Method | Endpoint | Description | Status Code |
|---|---|---|---|
| `GET` | `/tasks/summary` | Dashboard statistics | `200` |
| `POST` | `/tasks/` | Create a new task | `201` |
| `GET` | `/tasks/` | Fetch all tasks (with optional filters) | `200` |
| `GET` | `/tasks/{id}` | Fetch a single task by ID | `200` |
| `PATCH` | `/tasks/{id}` | Partially update a task | `200` |
| `DELETE` | `/tasks/{id}` | Delete a task | `200` |

---

### `GET /tasks/summary`

Returns live dashboard statistics. No parameters required.

**Response:**
```json
{
  "total": 12,
  "pending": 7,
  "completed": 5,
  "overdue": 2,
  "high_priority_pending": 3
}
```

---

### `POST /tasks/`

Creates a new task.

**Request body:**

| Field | Type | Required | Description |
|---|---|---|---|
| `title` | `string` | ✅ Yes | 1–100 characters |
| `description` | `string` | ❌ No | Up to 500 characters |
| `priority` | `string` | ❌ No | `low` \| `medium` (default) \| `high` |
| `due_date` | `string` | ❌ No | Format: `YYYY-MM-DD` |

**Example request:**
```json
{
  "title": "Submit project report",
  "description": "Include Q3 analysis",
  "priority": "high",
  "due_date": "2025-09-30"
}
```

**Example response `201`:**
```json
{
  "id": 1,
  "title": "Submit project report",
  "description": "Include Q3 analysis",
  "priority": "high",
  "completed": false,
  "due_date": "2025-09-30",
  "is_overdue": false
}
```

---

### `GET /tasks/`

Fetch tasks with optional filters and pagination.

**Query parameters:**

| Param | Type | Example | Description |
|---|---|---|---|
| `priority` | `string` | `?priority=high` | Filter by priority level |
| `completed` | `boolean` | `?completed=false` | Filter by completion status |
| `search` | `string` | `?search=report` | Search in title and description |
| `page` | `integer` | `?page=2` | Page number (default: `1`) |
| `limit` | `integer` | `?limit=5` | Results per page (default: `10`, max: `100`) |

**Combined example:**
```
GET /tasks/?priority=high&completed=false&search=report&page=1&limit=5
```

---

### `GET /tasks/{id}`

Fetch one task by its numeric ID.

**Example response `200`:**
```json
{
  "id": 3,
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "priority": "medium",
  "completed": false,
  "due_date": "2025-08-01",
  "is_overdue": true
}
```

Returns `404` if the ID does not exist.

---

### `PATCH /tasks/{id}`

Partially update a task. Only fields included in the request body are changed — all others remain untouched.

**Example request (mark as done and update due date):**
```json
{
  "completed": true,
  "due_date": "2025-10-15"
}
```

Returns `404` if the ID does not exist.

---

### `DELETE /tasks/{id}`

Permanently deletes the task with the given ID.

**Example response `200`:**
```json
{
  "message": "Task 3 deleted successfully."
}
```

Returns `404` if the ID does not exist.

---

## 📦 Pydantic Schemas

### `TaskCreate` — used for `POST`

```python
class TaskCreate(BaseModel):
    title:       str            # required, 1–100 chars
    description: Optional[str] # optional, max 500 chars
    priority:    Priority       # "low" | "medium" | "high", default "medium"
    due_date:    Optional[date] # optional, YYYY-MM-DD
```

### `TaskUpdate` — used for `PATCH`

All fields are optional. Only fields you provide will be updated.

```python
class TaskUpdate(BaseModel):
    title:       Optional[str]
    description: Optional[str]
    priority:    Optional[Priority]
    completed:   Optional[bool]
    due_date:    Optional[date]
```

### `TaskResponse` — returned by the API

```python
class TaskResponse(BaseModel):
    id:          int
    title:       str
    description: Optional[str]
    priority:    Priority
    completed:   bool
    due_date:    Optional[date]
    is_overdue:  bool           # computed on read, not stored in DB
```

> `is_overdue` is `True` when `due_date` is in the past AND the task is not yet completed.

### `SummaryResponse` — returned by `/tasks/summary`

```python
class SummaryResponse(BaseModel):
    total:                 int
    pending:               int
    completed:             int
    overdue:               int
    high_priority_pending: int
```

---

## 🖥️ Console Client — Feature Guide

Run `python client.py` to launch the interactive menu. The dashboard is shown **automatically on startup and refreshed after every action**.

### Dashboard

```
╔══════════════════════════════════════════════╗
║              📊  TASK DASHBOARD              ║
╚══════════════════════════════════════════════╝

  Total tasks   :  12
  Pending       :  7
  Completed     :  5
  Overdue       :  2 overdue
  High priority :  3 high-priority

  Progress      ████████░░░░░░░░░░░░  41%
```

### Menu Options

| Option | Action |
|---|---|
| `1` | Create a new task (title, description, priority, due date) |
| `2` | View / filter tasks — prompts for optional filters before fetching |
| `3` | Fetch a single task by its ID |
| `4` | Update a task — shows current values first, update only what you change |
| `5` | Delete a task — shows full task preview before asking for confirmation |
| `0` | Exit |

### Overdue highlighting

Tasks past their due date that are not yet completed are flagged with a red `OVERDUE` badge in the terminal:

```
⬜ [4] Submit quarterly report   OVERDUE
     📝 Include Q3 analysis
     🔴 Priority: HIGH  📅 Due: 2025-08-01
```

### Filtering (option 2)

When you choose "View / filter tasks", the client prompts for each filter one by one. Press Enter to skip any you don't need:

```
▸ Filter by priority [low / medium / high]:  high
▸ Filter by status   [done / pending]:        pending
▸ Search keyword:                             report
▸ Page number (default 1):
▸ Results per page (default 10):
```

---

## 🗄️ Database

The app uses **SQLite** via SQLAlchemy ORM. The database file `todo.db` is created automatically in the project root on first run. No setup or migration commands are needed.

### Task table schema

| Column | Type | Notes |
|---|---|---|
| `id` | `INTEGER` | Primary key, auto-increment |
| `title` | `VARCHAR(100)` | Not null |
| `description` | `VARCHAR(500)` | Nullable |
| `priority` | `ENUM` | `low`, `medium`, `high` |
| `completed` | `BOOLEAN` | Default `false` |
| `due_date` | `DATE` | Nullable, `YYYY-MM-DD` |

> `is_overdue` is **not stored** — it is computed at the data access layer every time a task is read.

---

## 🔌 Architecture Overview

```
client.py  ──HTTP──▶  routers/tasks.py  ──calls──▶  database.py  ──ORM──▶  models.py  ──▶  todo.db
                            │                             │
                      schemas.py                   db_session.py
                    (validation)               (engine + get_db)
```

- **Router** — handles HTTP, validates with Pydantic, delegates to the DB layer
- **Database layer** — pure Python functions, no HTTP awareness
- **Models** — SQLAlchemy ORM classes, one per table
- **Schemas** — Pydantic models, fully decoupled from ORM
- **db_session** — engine and dependency injector, imported by both router and main

---

## 📝 Notes

- Data **persists across server restarts** in `todo.db`.
- Delete `todo.db` to wipe all data and start fresh.
- Pydantic v2 is required — the schemas use `model_config` and `model_dump()`.
- The server must be running before launching `client.py`.