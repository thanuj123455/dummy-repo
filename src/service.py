"""Service layer for the data2 MCP server.

This module implements the core logic to interact with the notes database
API. Each method corresponds to one tool in the MCP interface, performing
the underlying HTTP requests and processing responses.

Resources (HTTP clients) are opened and closed per call to ensure statelessness.
"""

from typing import Any, Dict, List, Optional
import httpx


class Data2Service:
    """Service class implementing operations against the notes database API."""

    async def search_notes(
        self,
        host: str,
        port: int,
        private_token: str,
        keyword: str,
        limit: Optional[int] = 10,
        max_rows: int = 1000,
    ) -> Dict[str, Any]:
        """
        Search notes whose title or body text contains the given keyword.

        Args:
            host: Base URL of the notes database service or API endpoint.
            port: Port number of the notes database service.
            private_token: Authentication token to access the notes database.
            keyword: Keyword to search for in note titles and text.
            limit: Maximum number of notes to return (default 10).
            max_rows: Absolute cap on rows returned to avoid overload (default 1000).

        Returns:
            A dict with status and a list of matching notes (id, title, snippet).
        """
        if limit is None:
            limit = 10
        if limit <= 0:
            raise ValueError("limit must be positive integer")

        if limit > max_rows:
            limit = max_rows

        base_url = f"{host}:{port}"
        search_endpoint = f"{base_url}/notes/search"

        headers = {"Authorization": f"Bearer {private_token}"}
        params = {"q": keyword, "limit": limit}

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(search_endpoint, headers=headers, params=params)

            response.raise_for_status()
            data = response.json()

            # Expected data format: list of notes with id, title, snippet
            # Defensive: validate that data is a list of dicts with required keys
            if not isinstance(data, list):
                raise RuntimeError("Unexpected response format: expected a list")

            notes: List[Dict[str, Any]] = []
            for item in data:
                if not isinstance(item, dict):
                    continue
                note_id = item.get("id")
                title = item.get("title")
                snippet = item.get("snippet") or item.get("excerpt") or ""
                if note_id is None or title is None:
                    continue
                notes.append({"id": str(note_id), "title": str(title), "snippet": str(snippet)})
                if len(notes) >= limit:
                    break

        return {"status": "success", "notes": notes}

    async def get_note(
        self,
        host: str,
        port: int,
        private_token: str,
        note_id: str,
    ) -> Dict[str, Any]:
        """
        Retrieve a single note by its unique ID.

        Args:
            host: Base URL of the notes database service or API endpoint.
            port: Port number of the notes database service.
            private_token: Authentication token to access the notes database.
            note_id: The unique identifier of the note to retrieve.

        Returns:
            A dict with status and the note details (id, title, body) on success.
        """
        base_url = f"{host}:{port}"
        note_endpoint = f"{base_url}/notes/{note_id}"

        headers = {"Authorization": f"Bearer {private_token}"}

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(note_endpoint, headers=headers)

            if response.status_code == 404:
                raise RuntimeError(f"Note with id {note_id!r} not found")

            response.raise_for_status()
            data = response.json()

            # Expected data format: dict with id, title, body
            if not isinstance(data, dict):
                raise RuntimeError("Unexpected response format: expected a dict")

            note_id_ret = data.get("id")
            title = data.get("title")
            body = data.get("body")

            if note_id_ret is None or title is None or body is None:
                raise RuntimeError("Incomplete note data received from API")

        return {
            "status": "success",
            "note": {"id": str(note_id_ret), "title": str(title), "body": str(body)},
        }

    async def create_note(
        self,
        host: str,
        port: int,
        private_token: str,
        title: str,
        body: str,
    ) -> Dict[str, Any]:
        """
        Add a new note with a given title and body text.

        Args:
            host: Base URL of the notes database service or API endpoint.
            port: Port number of the notes database service.
            private_token: Authentication token to access the notes database.
            title: Title of the new note.
            body: Text body content of the new note.

        Returns:
            A dict with status and the new note's id on success.
        """
        base_url = f"{host}:{port}"
        create_endpoint = f"{base_url}/notes"

        headers = {
            "Authorization": f"Bearer {private_token}",
            "Content-Type": "application/json",
        }
        json_body = {"title": title, "body": body}

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(create_endpoint, headers=headers, json=json_body)

            response.raise_for_status()
            data = response.json()

            # Expecting a dict with the new note's id
            new_note_id = data.get("id")
            if new_note_id is None:
                raise RuntimeError("API did not return new note id")

        return {"status": "success", "note_id": str(new_note_id)}