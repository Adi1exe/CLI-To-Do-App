import requests
import json

BASE_URL = "http://127.0.0.1:8000/tasks"

PRIORITY_COLORS = {"high": "\033[91m", "medium": "\033[93m", "low": "\033[92m"}
RESET  = "\033[0m"
BOLD   = "\033[1m"
CYAN   = "\033[96m"
GREEN  = "\033[92m"
RED    = "\033[91m"

def print_task(task: dict):
    color = PRIORITY_COLORS.get(task.get("priority", "medium"), "")
    done  = "✅" if task.get("completed") else "⬜"
    print(f"\n  {done} [{BOLD}{task['id']}{RESET}] {BOLD}{task['title']}{RESET}")
    if task.get("description"):
        print(f"       📝 {task['description']}")
    print(f"       {color}Priority: {task['priority'].upper()}{RESET}")


def print_separator():
    print(f"\n{CYAN}{'─' * 50}{RESET}")


def prompt(msg: str) -> str:
    return input(f"  {BOLD}▸ {msg}{RESET}").strip()

def create_task():
    print_separator()
    print(f"{BOLD}  ➕  CREATE TASK{RESET}")
    title       = prompt("Title: ")
    description = prompt("Description (optional, press Enter to skip): ")
    priority    = prompt("Priority [low / medium / high] (default: medium): ") or "medium"

    if priority not in ("low", "medium", "high"):
        print(f"{RED}  Invalid priority. Defaulting to 'medium'.{RESET}")
        priority = "medium"

    payload = {"title": title, "priority": priority}
    if description:
        payload["description"] = description

    r = requests.post(BASE_URL + "/", json=payload)
    if r.status_code == 201:
        print(f"{GREEN}  Task created!{RESET}")
        print_task(r.json())
    else:
        print(f"{RED}  Error: {r.json()}{RESET}")

def fetch_all_tasks():
    print_separator()
    print(f"{BOLD}  📋  ALL TASKS{RESET}")
    r = requests.get(BASE_URL + "/")
    tasks = r.json()
    if not tasks:
        print("  (no tasks found)")
        return
    for t in tasks:
        print_task(t)

def fetch_task_by_id():
    print_separator()
    print(f"{BOLD}  🔍  FETCH TASK BY ID{RESET}")
    task_id = prompt("Task ID: ")
    r = requests.get(f"{BASE_URL}/{task_id}")
    if r.status_code == 200:
        print_task(r.json())
    else:
        print(f"{RED}  {r.json().get('detail', 'Error')}{RESET}")

def update_task():
    print_separator()
    print(f"{BOLD}  ✏️   UPDATE TASK{RESET}")
    task_id = prompt("Task ID to update: ")

    r = requests.get(f"{BASE_URL}/{task_id}")
    if r.status_code != 200:
        print(f"{RED}  {r.json().get('detail', 'Error')}{RESET}")
        return
    print("  Current task:")
    print_task(r.json())

    print("\n  (leave blank to keep current value)")
    title       = prompt("New title: ")
    description = prompt("New description: ")
    priority    = prompt("New priority [low / medium / high]: ")
    completed   = prompt("Mark as completed? [y / n]: ")

    payload = {}
    if title:       payload["title"]       = title
    if description: payload["description"] = description
    if priority in ("low", "medium", "high"):
        payload["priority"] = priority
    if completed.lower() == "y":
        payload["completed"] = True
    elif completed.lower() == "n":
        payload["completed"] = False

    if not payload:
        print("  Nothing to update.")
        return

    r = requests.patch(f"{BASE_URL}/{task_id}", json=payload)
    if r.status_code == 200:
        print(f"{GREEN}  Task updated!{RESET}")
        print_task(r.json())
    else:
        print(f"{RED}  {r.json().get('detail', 'Error')}{RESET}")


def delete_task():
    print_separator()
    print(f"{BOLD}  🗑️   DELETE TASK{RESET}")
    task_id = prompt("Task ID to delete: ")
    confirm = prompt(f"Are you sure you want to delete task {task_id}? [y/n]: ")
    if confirm.lower() != "y":
        print("  Cancelled.")
        return
    r = requests.delete(f"{BASE_URL}/{task_id}")
    if r.status_code == 200:
        print(f"{GREEN}  {r.json()['message']}{RESET}")
    else:
        print(f"{RED}  {r.json().get('detail', 'Error')}{RESET}")


MENU = """
{cyan}{bold}╔══════════════════════════════╗
║     📝  To-Do CLI Client     ║
╚══════════════════════════════╝{reset}

  {bold}1.{reset} ➕  Create task
  {bold}2.{reset} 📋  View all tasks
  {bold}3.{reset} 🔍  Fetch task by ID
  {bold}4.{reset} ✏️   Update task
  {bold}5.{reset} 🗑️   Delete task
  {bold}0.{reset} 🚪  Exit
"""

def main():
    print(MENU.format(cyan=CYAN, bold=BOLD, reset=RESET))
    while True:
        choice = prompt("Choose an option: ")
        if choice == "1":
            create_task()
        elif choice == "2":
            fetch_all_tasks()
        elif choice == "3":
            fetch_task_by_id()
        elif choice == "4":
            update_task()
        elif choice == "5":
            delete_task()
        elif choice == "0":
            print(f"\n  {GREEN}Goodbye! 👋{RESET}\n")
            break
        else:
            print(f"{RED}  Invalid choice. Try again.{RESET}")

        print(MENU.format(cyan=CYAN, bold=BOLD, reset=RESET))

if __name__ == "__main__":
    main()