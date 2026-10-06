"""Tests for todo-tasks MCP tools in todo_tasks_mcp.py.

These tests mock the service layer to verify tool behavior without
network or credentials. They cover success and failure cases for at least
two tools, calling the async tool functions directly.
"""

import pytest
from unittest.mock import patch
from pydantic import SecretStr

from todo_tasks_mcp import create_task, list_tasks, complete_task
from src.service import TaskNotFoundError


@pytest.mark.asyncio
@patch("todo_tasks_mcp._service.create_task")
async def test_create_task_success(mock_create_task):
    mock_create_task.return_value = {
        "id": "1234",
        "title": "Test Task",
        "description": "A test description",
        "completed": False,
    }
    result = await create_task(
        github_token=SecretStr("fake-token"),
        repository_url="owner/repo",
        branch="main",
        title="Test Task",
        description="A test description",
    )
    assert result["status"] == "success"
    assert result["id"] == "1234"
    assert result["title"] == "Test Task"
    assert result["description"] == "A test description"
    assert result["completed"] is False
    mock_create_task.assert_called_once_with(
        github_token="fake-token",
        repository_url="owner/repo",
        branch="main",
        title="Test Task",
        description="A test description",
    )


@pytest.mark.asyncio
@patch("todo_tasks_mcp._service.create_task")
async def test_create_task_failure(mock_create_task):
    mock_create_task.side_effect = ValueError("Invalid title")
    result = await create_task(
        github_token=SecretStr("fake-token"),
        repository_url="owner/repo",
        branch=None,
        title="   ",
        description=None,
    )
    assert result["status"] == "failed"
    assert "Invalid title" in result["message"]
    mock_create_task.assert_called_once()


@pytest.mark.asyncio
@patch("todo_tasks_mcp._service.list_tasks")
async def test_list_tasks_success(mock_list_tasks):
    mock_list_tasks.return_value = [
        {
            "id": "1",
            "title": "Task One",
            "description": "First task",
            "completed": False,
        },
        {
            "id": "2",
            "title": "Task Two",
            "description": "",
            "completed": True,
        },
    ]
    result = await list_tasks(
        github_token=SecretStr("fake-token"),
        repository_url="owner/repo",
        branch=None,
    )
    assert result["status"] == "success"
    assert isinstance(result["tasks"], list)
    assert len(result["tasks"]) == 2
    assert result["tasks"][0]["id"] == "1"
    assert result["tasks"][1]["completed"] is True
    mock_list_tasks.assert_called_once_with(
        github_token="fake-token",
        repository_url="owner/repo",
        branch=None,
    )


@pytest.mark.asyncio
@patch("todo_tasks_mcp._service.list_tasks")
async def test_list_tasks_failure(mock_list_tasks):
    mock_list_tasks.side_effect = RuntimeError("Service failure")
    result = await list_tasks(
        github_token=SecretStr("fake-token"),
        repository_url="owner/repo",
        branch="dev",
    )
    assert result["status"] == "failed"
    assert "Service failure" in result["message"]
    mock_list_tasks.assert_called_once()


@pytest.mark.asyncio
@patch("todo_tasks_mcp._service.complete_task")
async def test_complete_task_success(mock_complete_task):
    mock_complete_task.return_value = None
    task_id = "task-123"
    result = await complete_task(
        github_token=SecretStr("fake-token"),
        repository_url="owner/repo",
        branch="feature",
        task_id=task_id,
    )
    assert result["status"] == "success"
    assert f"Task {task_id} marked as completed" in result["message"]
    mock_complete_task.assert_called_once_with(
        github_token="fake-token",
        repository_url="owner/repo",
        branch="feature",
        task_id=task_id,
    )


@pytest.mark.asyncio
@patch("todo_tasks_mcp._service.complete_task")
async def test_complete_task_not_found(mock_complete_task):
    mock_complete_task.side_effect = TaskNotFoundError("Task with id 'missing' not found")
    result = await complete_task(
        github_token=SecretStr("fake-token"),
        repository_url="owner/repo",
        branch=None,
        task_id="missing",
    )
    assert result["status"] == "failed"
    assert "not found" in result["message"]
    mock_complete_task.assert_called_once()


@pytest.mark.asyncio
@patch("todo_tasks_mcp._service.complete_task")
async def test_complete_task_other_failure(mock_complete_task):
    mock_complete_task.side_effect = RuntimeError("Unexpected error")
    result = await complete_task(
        github_token=SecretStr("fake-token"),
        repository_url="owner/repo",
        branch=None,
        task_id="task-999",
    )
    assert result["status"] == "failed"
    assert "Unexpected error" in result["message"]
    mock_complete_task.assert_called_once()