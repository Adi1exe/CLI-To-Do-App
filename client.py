"""
Console Client for the To-Do API  v2
─────────────────────────────────────
Run AFTER the server is up:  python client.py
"""

import requests
from datetime import date

BASE_URL = "http://127.0.0.1:8000/tasks"

# ─── ANSI colours ─────────────────────────────────────────────────────────────
RESET   = "\033[0m"
BOLD    = "\033[1m"
DIM     = "\033[2m"
CYAN    = "\033[96m"
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
RED     = "\033[91m"
MAGENTA = "\033[95m"
WHITE   = "\033[97m"
BG_RED  = "\033[41m"

PRIORITY_COLOR = {"high": RED, "medium": YELLOW, "low": GREEN}
PRIORITY_ICON  = {"high": "🔴", "medium": "🟡", "low": "🟢"}


# ─── Helpers ──────────────────────────────────────────────────────────────────

def prompt(msg: str) -> str:
    return input(f"  {BOLD}▸ {msg}{RESET}").strip()

def print_separator(title: str = ""):
    line = "─" * 50
    if title:
        print(f"\n{CYAN}{line}{RESET}")
        print(f"{BOLD}  {title}{RESET}")
    else:
        print(f"\n{CYAN}{line}{RESET}")

def print_task(task: dict):
    done      = "✅" if task.get("completed") else "⬜"
    p         = task.get("priority", "medium")
    pcolor    = PRIORITY_COLOR.get(p, "")
    picon     = PRIORITY_ICON.get(p, "")
    overdue   = task.get("is_overdue", False)
    due       = task.get("due_date")

    # Title line
    overdue_tag = f"  {BG_RED}{WHITE} OVERDUE {RESET}" if overdue else ""
    print(f"\n  {done} [{BOLD}{task['id']}{RESET}] {BOLD}{task['title']}{RESET}{overdue_tag}")

    if task.get("description"):
        print(f"       {DIM}📝 {task['description']}{RESET}")

    due_str = f"  📅 Due: {due}" if due else ""
    print(f"       {pcolor}{picon} Priority: {p.upper()}{RESET}{due_str}")


def _safe_get(url: str, **kwargs):
    try:
        return requests.get(url, **kwargs)
    except requests.ConnectionError:
        print(f"\n{RED}  ✖  Cannot reach the server at {BASE_URL}.")
        print(f"     Make sure the server is running: python run.py{RESET}")
        return None


# ─── 1. DASHBOARD ─────────────────────────────────────────────────────────────

def show_dashboard():
    r = _safe_get(f"{BASE_URL}/summary")
    if r is None or r.status_code != 200:
        return

    s = r.json()
    total     = s["total"]
    pending   = s["pending"]
    completed = s["completed"]
    overdue   = s["overdue"]
    high_pend = s["high_priority_pending"]

    pct_done  = int((completed / total * 100)) if total else 0
    bar_done  = "█" * (pct_done // 5)
    bar_empty = "░" * (20 - len(bar_done))

    overdue_str   = f"{RED}{overdue} overdue{RESET}"   if overdue   else f"{GREEN}0 overdue{RESET}"
    high_str      = f"{RED}{high_pend} high‑priority{RESET}" if high_pend else f"{GREEN}0 high‑priority{RESET}"

    print(f"""
{CYAN}{BOLD}╔══════════════════════════════════════════════╗
║              📊  TASK DASHBOARD              ║
╚══════════════════════════════════════════════╝{RESET}

  {BOLD}Total tasks   :{RESET}  {total}
  {BOLD}Pending       :{RESET}  {YELLOW}{pending}{RESET}
  {BOLD}Completed     :{RESET}  {GREEN}{completed}{RESET}
  {BOLD}Overdue       :{RESET}  {overdue_str}
  {BOLD}High priority :{RESET}  {high_str}

  {BOLD}Progress  {RESET}  {GREEN}{bar_done}{RESET}{DIM}{bar_empty}{RESET}  {pct_done}%
""")


# ─── 2. CREATE ────────────────────────────────────────────────────────────────

def create_task():
    print_separator("➕  CREATE TASK")
    title = prompt("Title: ")
    if not title:
        print(f"{RED}  Title cannot be empty.{RESET}")
        return

    description = prompt("Description (optional): ")
    priority    = prompt("Priority [low / medium / high] (default: medium): ") or "medium"
    if priority not in ("low", "medium", "high"):
        print(f"{YELLOW}  Invalid priority — defaulting to 'medium'.{RESET}")
        priority = "medium"

    due_raw = prompt("Due date YYYY-MM-DD (optional): ")
    payload = {"title": title, "priority": priority}
    if description: payload["description"] = description
    if due_raw:     payload["due_date"] = due_raw

    r = requests.post(BASE_URL + "/", json=payload)
    if r.status_code == 201:
        print(f"{GREEN}  Task created!{RESET}")
        print_task(r.json())
    else:
        _print_error(r)


# ─── 3. VIEW ALL (with filters) ───────────────────────────────────────────────

def fetch_all_tasks():
    print_separator("📋  VIEW TASKS")

    print(f"  {DIM}(Press Enter to skip any filter){RESET}")
    priority  = prompt("Filter by priority [low / medium / high]: ")
    completed = prompt("Filter by status   [done / pending]:      ")
    search    = prompt("Search keyword                          :  ")
    page      = prompt("Page number (default 1)                 :  ") or "1"
    limit     = prompt("Results per page (default 10)           :  ") or "10"

    params = {"page": page, "limit": limit}
    if priority in ("low", "medium", "high"): params["priority"]  = priority
    if completed == "done":    params["completed"] = "true"
    if completed == "pending": params["completed"] = "false"
    if search:                 params["search"]    = search

    r = _safe_get(BASE_URL + "/", params=params)
    if r is None: return

    tasks = r.json()
    if not tasks:
        print(f"\n  {DIM}No tasks match your filters.{RESET}")
        return

    overdue_count = sum(1 for t in tasks if t.get("is_overdue"))
    print(f"\n  {BOLD}{len(tasks)} task(s) found{RESET}", end="")
    if overdue_count:
        print(f"  {RED}({overdue_count} overdue){RESET}", end="")
    print()

    for t in tasks:
        print_task(t)


# ─── 4. FETCH BY ID ───────────────────────────────────────────────────────────

def fetch_task_by_id():
    print_separator("🔍  FETCH TASK BY ID")
    task_id = prompt("Task ID: ")
    r = _safe_get(f"{BASE_URL}/{task_id}")
    if r is None: return
    if r.status_code == 200:
        print_task(r.json())
    else:
        _print_error(r)


# ─── 5. UPDATE ────────────────────────────────────────────────────────────────

def update_task():
    print_separator("✏️   UPDATE TASK")
    task_id = prompt("Task ID to update: ")

    r = _safe_get(f"{BASE_URL}/{task_id}")
    if r is None: return
    if r.status_code != 200:
        _print_error(r)
        return

    print(f"\n  {BOLD}Current task:{RESET}")
    print_task(r.json())

    print(f"\n  {DIM}(Leave blank to keep current value){RESET}")
    title       = prompt("New title         : ")
    description = prompt("New description   : ")
    priority    = prompt("New priority [low / medium / high]: ")
    due_raw     = prompt("New due date YYYY-MM-DD            : ")
    completed   = prompt("Mark as completed? [y / n]         : ")

    payload = {}
    if title:   payload["title"]       = title
    if description: payload["description"] = description
    if priority in ("low", "medium", "high"): payload["priority"] = priority
    if due_raw: payload["due_date"]    = due_raw
    if completed.lower() == "y": payload["completed"] = True
    if completed.lower() == "n": payload["completed"] = False

    if not payload:
        print(f"  {DIM}Nothing to update.{RESET}")
        return

    r = requests.patch(f"{BASE_URL}/{task_id}", json=payload)
    if r.status_code == 200:
        print(f"{GREEN}  Task updated!{RESET}")
        print_task(r.json())
    else:
        _print_error(r)


# ─── 6. DELETE ────────────────────────────────────────────────────────────────

def delete_task():
    print_separator("🗑️   DELETE TASK")
    task_id = prompt("Task ID to delete: ")

    r = _safe_get(f"{BASE_URL}/{task_id}")
    if r is None: return
    if r.status_code != 200:
        _print_error(r)
        return

    print(f"\n  {BOLD}About to delete:{RESET}")
    print_task(r.json())

    confirm = prompt(f"\n  Confirm delete? [y/n]: ")
    if confirm.lower() != "y":
        print(f"  {DIM}Cancelled.{RESET}")
        return

    r = requests.delete(f"{BASE_URL}/{task_id}")
    if r.status_code == 200:
        print(f"{GREEN}  {r.json()['message']}{RESET}")
    else:
        _print_error(r)


# ─── Error helper ─────────────────────────────────────────────────────────────

def _print_error(r):
    try:
        detail = r.json().get("detail", r.text)
    except Exception:
        detail = r.text
    print(f"{RED}  ✖  {detail}{RESET}")


# ─── Menu ─────────────────────────────────────────────────────────────────────

MENU = """{cyan}{bold}╔══════════════════════════════════════════════╗
║            📝  To-Do CLI  v2                 ║
╚══════════════════════════════════════════════╝{reset}

  {bold}1.{reset} ➕  Create task
  {bold}2.{reset} 📋  View / filter tasks
  {bold}3.{reset} 🔍  Fetch task by ID
  {bold}4.{reset} ✏️   Update task
  {bold}5.{reset} 🗑️   Delete task
  {bold}0.{reset} 🚪  Exit
"""

def main():
    # Show dashboard immediately on launch
    show_dashboard()

    print(MENU.format(cyan=CYAN, bold=BOLD, reset=RESET))
    while True:
        choice = prompt("Choose an option: ")
        if   choice == "1": create_task()
        elif choice == "2": fetch_all_tasks()
        elif choice == "3": fetch_task_by_id()
        elif choice == "4": update_task()
        elif choice == "5": delete_task()
        elif choice == "0":
            print(f"\n  {GREEN}Goodbye! 👋{RESET}\n")
            break
        else:
            print(f"{RED}  Invalid choice.{RESET}")

        # Refresh dashboard after every action
        show_dashboard()
        print(MENU.format(cyan=CYAN, bold=BOLD, reset=RESET))


if __name__ == "__main__":
    main()