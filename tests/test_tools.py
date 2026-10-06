import pytest
from unittest.mock import patch

from demo_notes_mcp import add_note_text, list_notes, delete_note_id


@pytest.mark.asyncio
@patch("src.service.DemoNotesService.add_note_text")
async def test_add_note_text_success(mock_add_note_text):
    mock_add_note_text.return_value = {"note_id": 123}

    result = await add_note_text(text="Test note")
    assert result == {"status": "success", "note_id": 123}
    mock_add_note_text.assert_called_once_with("Test note")


@pytest.mark.asyncio
@patch("src.service.DemoNotesService.add_note_text")
async def test_add_note_text_failure(mock_add_note_text):
    mock_add_note_text.side_effect = ValueError("Invalid text")

    result = await add_note_text(text="Invalid note")
    assert result["status"] == "failed"
    assert "Invalid text" in result["message"]
    mock_add_note_text.assert_called_once_with("Invalid note")


@pytest.mark.asyncio
@patch("src.service.DemoNotesService.list_notes")
async def test_list_notes_success(mock_list_notes):
    mock_list_notes.return_value = [
        {"id": 1, "text": "Note 1"},
        {"id": 2, "text": "Note 2"},
    ]

    result = await list_notes()
    assert result == {
        "status": "success",
        "notes": [
            {"id": 1, "text": "Note 1"},
            {"id": 2, "text": "Note 2"},
        ],
    }
    mock_list_notes.assert_called_once_with()


@pytest.mark.asyncio
@patch("src.service.DemoNotesService.list_notes")
async def test_list_notes_failure(mock_list_notes):
    mock_list_notes.side_effect = RuntimeError("Storage unavailable")

    result = await list_notes()
    assert result["status"] == "failed"
    assert "Storage unavailable" in result["message"]
    mock_list_notes.assert_called_once_with()


@pytest.mark.asyncio
@patch("src.service.DemoNotesService.delete_note_id")
async def test_delete_note_id_success(mock_delete_note_id):
    mock_delete_note_id.return_value = {"message": "Note with ID 5 deleted successfully"}

    result = await delete_note_id(note_id=5)
    assert result == {
        "status": "success",
        "message": "Note with ID 5 deleted successfully",
    }
    mock_delete_note_id.assert_called_once_with(5)


@pytest.mark.asyncio
@patch("src.service.DemoNotesService.delete_note_id")
async def test_delete_note_id_failure(mock_delete_note_id):
    mock_delete_note_id.side_effect = KeyError("Note with ID 99 not found")

    result = await delete_note_id(note_id=99)
    assert result["status"] == "failed"
    assert "Note with ID 99 not found" in result["message"]
    mock_delete_note_id.assert_called_once_with(99)