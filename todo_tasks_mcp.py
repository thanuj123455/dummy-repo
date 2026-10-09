"""todo_tasks_mcp.py: FastMCP tools adapters for the todo-tasks server."""

from typing import Optional
from fastmcp import FastMCP
from pydantic import Field, SecretStr

from src.service import TaskService, TaskNotFoundError

mcp = FastMCP("todo-tasks")
_service = TaskService()


def _error(exc: Exception) -> dict:
    return {"status": "failed", "message": str(exc)}


@mcp.tool(
    name="create_task",
    title="Create Task",
    description="Creates a new to-do task with a title and optional description.",
)
async def create_task(
    github_token: SecretStr = Field(
        ...,
        description="GitHub personal access token",
        json_schema_extra={"format": "password", "ui_type": "password"},
    ),
    repository_url: str = Field(..., description="Repository as 'owner/repo' or a full GitHub URL"),
    branch: Optional[str] = Field(None, description="Branch whose file tree is extracted (optional)"),
    title: str = Field(..., description="Title of the task to create"),
    description: Optional[str] = Field(None, description="Optional detailed description of the task"),
) -> dict:
    """
    Create a new task with the given title and optional description.
    Returns a status envelope with the created task's ID and details on success.
    """
    try:
        result = _service.create_task(
            github_token=github_token.get_secret_value(),
            repository_url=repository_url,
            branch=branch,
            title=title,
            description=description,
        )
        return {"status": "success", **result}
    except Exception as exc:
        return _error(exc)


@mcp.tool(
    name="list_tasks",
    title="List Tasks",
    description="Lists all to-do tasks, including their completion status.",
)
async def list_tasks(
    github_token: SecretStr = Field(
        ...,
        description="GitHub personal access token",
        json_schema_extra={"format": "password", "ui_type": "password"},
    ),
    repository_url: str = Field(..., description="Repository as 'owner/repo' or a full GitHub URL"),
    branch: Optional[str] = Field(None, description="Branch whose file tree is extracted (optional)"),
) -> dict:
    """
    List all tasks for the given connection context.
    Returns a status envelope with a list of all tasks and their status.
    """
    try:
        tasks = _service.list_tasks(
            github_token=github_token.get_secret_value(),
            repository_url=repository_url,
            branch=branch,
        )
        return {"status": "success", "tasks": tasks}
    except Exception as exc:
        return _error(exc)


@mcp.tool(
    name="complete_task",
    title="Complete Task",
    description="Marks a specified to-do task as completed.",
)
async def complete_task(
    github_token: SecretStr = Field(
        ...,
        description="GitHub personal access token",
        json_schema_extra={"format": "password", "ui_type": "password"},
    ),
    repository_url: str = Field(..., description="Repository as 'owner/repo' or a full GitHub URL"),
    branch: Optional[str] = Field(None, description="Branch whose file tree is extracted (optional)"),
    task_id: str = Field(..., description="ID of the task to mark as completed"),
) -> dict:
    """
    Mark the specified task as completed.
    Returns a status envelope indicating success or failure of the operation.
    """
    try:
        _service.complete_task(
            github_token=github_token.get_secret_value(),
            repository_url=repository_url,
            branch=branch,
            task_id=task_id,
        )
        return {"status": "success", "message": f"Task {task_id} marked as completed"}
    except TaskNotFoundError as exc:
        return {"status": "failed", "message": str(exc)}
    except Exception as exc:
        return _error(exc)