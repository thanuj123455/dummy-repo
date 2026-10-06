"""demo-notes MCP server tools module.

Thin FastMCP adapter layer over the demo-notes service layer.
"""

from typing import Any, Dict, List

from fastmcp import FastMCP
from pydantic import Field, SecretStr

from src.service import DemoNotesService

mcp = FastMCP("demo-notes")


@mcp.tool(
    name="add_note_text",
    title="Add Note Text",
    description="Add a short text note to the in-memory notes list.",
)
async def add_note_text(
    text: str = Field(..., description="The text content of the note to add"),
) -> Dict[str, Any]:
    """
    Add a short text note to the in-memory notes list.

    Args:
        text: The text content of the note to add.

    Returns:
        A dict with status 'success' and the integer ID of the newly added note.
        On failure, returns status 'failed' and a message.
    """
    try:
        result = DemoNotesService.add_note_text(text)
        return {"status": "success", "note_id": result["note_id"]}
    except Exception as exc:
        return {"status": "failed", "message": str(exc)}


@mcp.tool(
    name="list_notes",
    title="List Notes",
    description="List all current notes stored in memory with their IDs and text.",
)
async def list_notes() -> Dict[str, Any]:
    """
    List all current notes stored in memory with their IDs and text.

    Returns:
        A dict with status 'success' and 'notes' which is a list of objects with 'id' and 'text'.
        On failure, returns status 'failed' and a message.
    """
    try:
        notes = DemoNotesService.list_notes()
        return {"status": "success", "notes": notes}
    except Exception as exc:
        return {"status": "failed", "message": str(exc)}


@mcp.tool(
    name="delete_note_id",
    title="Delete Note By ID",
    description="Delete a note by its unique ID from the in-memory notes list.",
)
async def delete_note_id(
    note_id: int = Field(..., description="The unique integer ID of the note to delete"),
) -> Dict[str, Any]:
    """
    Delete a note by its unique ID from the in-memory notes list.

    Args:
        note_id: The unique integer ID of the note to delete.

    Returns:
        A dict with status 'success' and a confirmation message on successful deletion.
        On failure, returns status 'failed' and a message.
    """
    try:
        result = DemoNotesService.delete_note_id(note_id)
        return {"status": "success", "message": result["message"]}
    except Exception as exc:
        return {"status": "failed", "message": str(exc)}