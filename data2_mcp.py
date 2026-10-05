"""data2 MCP tools module.

Defines the FastMCP instance and all tools (search_notes, get_note, create_note).
Each tool is a thin adapter over the service layer in src.service.py.
"""

from typing import Any, Dict, Optional

from fastmcp import FastMCP
from pydantic import Field, SecretStr

from src.service import Data2Service

mcp = FastMCP("data2")
_service = Data2Service()


def _error(exc: Exception) -> Dict[str, Any]:
    """Return a failed status envelope with the exception message."""
    return {"status": "failed", "message": str(exc)}


@mcp.tool(
    name="search_notes",
    title="Search Notes",
    description=(
        "Search notes whose title or body text contains the given keyword. "
        "Returns a list of matching notes with their IDs, titles, and excerpts."
    ),
)
async def search_notes(
    host: str = Field(..., description="The base URL of the notes database service or API endpoint"),
    port: int = Field(..., description="The port number of the notes database service"),
    private_token: SecretStr = Field(
        ..., description="Authentication token (GitLab private/personal access token) to access the notes database",
        json_schema_extra={"format": "password", "ui_type": "password"},
    ),
    keyword: str = Field(..., description="Keyword to search for in note titles and text"),
    limit: Optional[int] = Field(10, description="Maximum number of notes to return (default 10)"),
) -> Dict[str, Any]:
    """
    Search notes whose title or body text contains the given keyword.

    Args:
        host: The base URL of the notes database service or API endpoint.
        port: The port number of the notes database service.
        private_token: Authentication token to access the notes database.
        keyword: Keyword to search for in note titles and text.
        limit: Maximum number of notes to return (default 10).

    Returns:
        A dictionary with status and a list of matching notes, each note including id, title, and snippet.
    """
    try:
        token_value = private_token.get_secret_value()
        result = await _service.search_notes(host, port, token_value, keyword, limit)
        return result
    except Exception as exc:
        return _error(exc)


@mcp.tool(
    name="get_note",
    title="Get Note",
    description=(
        "Retrieve a single note by its unique ID. Returns the note's id, title, and full text body."
    ),
)
async def get_note(
    host: str = Field(..., description="The base URL of the notes database service or API endpoint"),
    port: int = Field(..., description="The port number of the notes database service"),
    private_token: SecretStr = Field(
        ..., description="Authentication token (GitLab private/personal access token) to access the notes database",
        json_schema_extra={"format": "password", "ui_type": "password"},
    ),
    note_id: str = Field(..., description="The unique identifier of the note to retrieve"),
) -> Dict[str, Any]:
    """
    Retrieve a single note by its unique ID.

    Args:
        host: The base URL of the notes database service or API endpoint.
        port: The port number of the notes database service.
        private_token: Authentication token to access the notes database.
        note_id: The unique identifier of the note to retrieve.

    Returns:
        A dictionary with status and the note details (id, title, body) on success.
    """
    try:
        token_value = private_token.get_secret_value()
        result = await _service.get_note(host, port, token_value, note_id)
        return result
    except Exception as exc:
        return _error(exc)


@mcp.tool(
    name="create_note",
    title="Create Note",
    description=(
        "Add a new note with a given title and body text. Returns the new note's id on success."
    ),
)
async def create_note(
    host: str = Field(..., description="The base URL of the notes database service or API endpoint"),
    port: int = Field(..., description="The port number of the notes database service"),
    private_token: SecretStr = Field(
        ..., description="Authentication token (GitLab private/personal access token) to access the notes database",
        json_schema_extra={"format": "password", "ui_type": "password"},
    ),
    title: str = Field(..., description="Title of the new note"),
    body: str = Field(..., description="Text body content of the new note"),
) -> Dict[str, Any]:
    """
    Add a new note with a given title and body text.

    Args:
        host: The base URL of the notes database service or API endpoint.
        port: The port number of the notes database service.
        private_token: Authentication token to access the notes database.
        title: Title of the new note.
        body: Text body content of the new note.

    Returns:
        A dictionary with status and the new note's id on success.
    """
    try:
        token_value = private_token.get_secret_value()
        result = await _service.create_note(host, port, token_value, title, body)
        return result
    except Exception as exc:
        return _error(exc)