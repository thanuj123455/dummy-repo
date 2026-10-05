import pytest
from unittest.mock import AsyncMock, patch
from pydantic import SecretStr

from data2_mcp import search_notes, get_note, create_note


@pytest.mark.asyncio
async def test_search_notes_success():
    mock_response = {
        "status": "success",
        "notes": [
            {"id": "1", "title": "Note 1", "snippet": "Snippet 1"},
            {"id": "2", "title": "Note 2", "snippet": "Snippet 2"},
        ],
    }
    with patch("data2_mcp._service.search_notes", new_callable=AsyncMock) as mock_search:
        mock_search.return_value = mock_response

        result = await search_notes(
            host="http://localhost",
            port=1234,
            private_token=SecretStr("token"),
            keyword="test",
            limit=2,
        )

        mock_search.assert_awaited_once_with("http://localhost", 1234, "token", "test", 2)
        assert result == mock_response


@pytest.mark.asyncio
async def test_search_notes_failure():
    with patch("data2_mcp._service.search_notes", new_callable=AsyncMock) as mock_search:
        mock_search.side_effect = RuntimeError("search error")

        result = await search_notes(
            host="http://localhost",
            port=1234,
            private_token=SecretStr("token"),
            keyword="fail",
        )

        mock_search.assert_awaited_once()
        assert result["status"] == "failed"
        assert "search error" in result["message"]


@pytest.mark.asyncio
async def test_get_note_success():
    mock_response = {
        "status": "success",
        "note": {"id": "abc", "title": "Title", "body": "Body content"},
    }
    with patch("data2_mcp._service.get_note", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_response

        result = await get_note(
            host="http://localhost",
            port=5678,
            private_token=SecretStr("token"),
            note_id="abc",
        )

        mock_get.assert_awaited_once_with("http://localhost", 5678, "token", "abc")
        assert result == mock_response


@pytest.mark.asyncio
async def test_get_note_failure():
    with patch("data2_mcp._service.get_note", new_callable=AsyncMock) as mock_get:
        mock_get.side_effect = RuntimeError("note not found")

        result = await get_note(
            host="http://localhost",
            port=5678,
            private_token=SecretStr("token"),
            note_id="missing",
        )

        mock_get.assert_awaited_once()
        assert result["status"] == "failed"
        assert "note not found" in result["message"]


@pytest.mark.asyncio
async def test_create_note_success():
    mock_response = {"status": "success", "note_id": "new123"}
    with patch("data2_mcp._service.create_note", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_response

        result = await create_note(
            host="http://localhost",
            port=9012,
            private_token=SecretStr("token"),
            title="New Note",
            body="Note body",
        )

        mock_create.assert_awaited_once_with("http://localhost", 9012, "token", "New Note", "Note body")
        assert result == mock_response


@pytest.mark.asyncio
async def test_create_note_failure():
    with patch("data2_mcp._service.create_note", new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = RuntimeError("creation failed")

        result = await create_note(
            host="http://localhost",
            port=9012,
            private_token=SecretStr("token"),
            title="Fail Note",
            body="Fail body",
        )

        mock_create.assert_awaited_once()
        assert result["status"] == "failed"
        assert "creation failed" in result["message"]