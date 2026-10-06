"""Core service layer for todo-tasks MCP server.

This module holds all the logic for creating, listing, and completing to-do
tasks. It does not handle secrets or environment variables; all connection
and authentication parameters are passed explicitly to each method.

The tasks are stored in-memory keyed by the unique combination of
(github_token, repository_url, branch), so each distinct "datasource" has
its own isolated task list.

No external network/database calls are made here; this is a simple example
to demonstrate structure and MCP patterns.
"""

from typing import Optional, Dict, List, Any
from threading import Lock
import uuid


class TaskNotFoundError(Exception):
    """Raised when a task ID is not found."""


class TaskService:
    """Service class managing to-do tasks per connection context.

    Each distinct combination of (github_token, repository_url, branch)
    has its own isolated task store.
    """

    # In-memory storage: mapping key -> list of tasks
    # Key is a tuple: (github_token, repository_url, branch)
    _storage: Dict[tuple[str, str, Optional[str]], List[Dict[str, Any]]] = {}
    _lock = Lock()

    MAX_LIST_TASKS = 1000  # Cap for list_tasks results

    def __init__(self) -> None:
        # No instance state; all shared class state
        pass

    def _get_storage_key(
        self, github_token: str, repository_url: str, branch: Optional[str]
    ) -> tuple[str, str, Optional[str]]:
        return (github_token, repository_url, branch)

    def create_task(
        self,
        github_token: str,
        repository_url: str,
        branch: Optional[str],
        title: str,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a new to-do task with a title and optional description.

        Returns the created task's ID and details.
        """
        if not title or not title.strip():
            raise ValueError("title must be a non-empty string")

        key = self._get_storage_key(github_token, repository_url, branch)

        task_id = str(uuid.uuid4())
        task = {
            "id": task_id,
            "title": title.strip(),
            "description": description.strip() if description else "",
            "completed": False,
        }

        with self._lock:
            tasks = self._storage.setdefault(key, [])
            tasks.append(task)

        return {
            "id": task_id,
            "title": task["title"],
            "description": task["description"],
            "completed": False,
        }

    def list_tasks(
        self,
        github_token: str,
        repository_url: str,
        branch: Optional[str],
    ) -> List[Dict[str, Any]]:
        """List all to-do tasks for the given connection context.

        Returns a list of task dicts with id, title, description, and completed status.

        Caps results at MAX_LIST_TASKS.
        """
        key = self._get_storage_key(github_token, repository_url, branch)
        with self._lock:
            tasks = self._storage.get(key, [])

            # Defensive slicing if task count exceeds cap
            limited_tasks = tasks[: self.MAX_LIST_TASKS]

            # Return copies to prevent accidental mutation by callers
            return [
                {
                    "id": t["id"],
                    "title": t["title"],
                    "description": t["description"],
                    "completed": t["completed"],
                }
                for t in limited_tasks
            ]

    def complete_task(
        self,
        github_token: str,
        repository_url: str,
        branch: Optional[str],
        task_id: str,
    ) -> None:
        """Mark the specified to-do task as completed.

        Raises TaskNotFoundError if the task ID is not found.
        """
        if not task_id or not task_id.strip():
            raise ValueError("task_id must be a non-empty string")

        key = self._get_storage_key(github_token, repository_url, branch)

        with self._lock:
            tasks = self._storage.get(key, [])
            for task in tasks:
                if task["id"] == task_id:
                    if task["completed"]:
                        # Already completed, no change needed
                        return
                    task["completed"] = True
                    return

        raise TaskNotFoundError(f"Task with id {task_id!r} not found")