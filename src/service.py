"""Service layer for demo-notes MCP server.

Holds the in-memory notes storage and implements the core logic for adding,
listing, and deleting notes. This class is instantiated once per server process,
and notes are stored in class-level state to persist across calls.

All methods are synchronous and raise exceptions on failure.
"""

from threading import Lock
from typing import List, Dict, Optional


class DemoNotesService:
    """Service holding the in-memory notes and providing note operations."""

    _notes: List[Dict[str, object]] = []
    _next_id: int = 1
    _lock = Lock()

    @classmethod
    def add_note_text(cls, text: str) -> Dict[str, int]:
        """
        Add a short text note to the in-memory notes list.

        Args:
            text: The text content of the note to add.

        Returns:
            A dict containing the integer ID of the newly added note.
        """
        if not isinstance(text, str):
            raise TypeError("text must be a string")
        if not text.strip():
            raise ValueError("text must not be empty or whitespace")

        with cls._lock:
            note_id = cls._next_id
            cls._notes.append({"id": note_id, "text": text})
            cls._next_id += 1

        return {"note_id": note_id}

    @classmethod
    def list_notes(cls, max_rows: Optional[int] = 1000) -> List[Dict[str, object]]:
        """
        List all current notes stored in memory with their IDs and text.

        Args:
            max_rows: Maximum number of notes to return (default 1000).

        Returns:
            List of notes dicts, each with 'id' (int) and 'text' (str).
        """
        if max_rows is not None and (not isinstance(max_rows, int) or max_rows <= 0):
            raise ValueError("max_rows must be a positive integer or None")

        with cls._lock:
            if max_rows is None:
                # Return all notes
                notes_copy = [note.copy() for note in cls._notes]
            else:
                notes_copy = [note.copy() for note in cls._notes[:max_rows]]

        return notes_copy

    @classmethod
    def delete_note_id(cls, note_id: int) -> Dict[str, str]:
        """
        Delete a note by its unique ID from the in-memory notes list.

        Args:
            note_id: The unique integer ID of the note to delete.

        Returns:
            A dict with a confirmation message on successful deletion.

        Raises:
            KeyError if the note ID is not found.
            TypeError if note_id is not an int.
        """
        if not isinstance(note_id, int):
            raise TypeError("note_id must be an integer")

        with cls._lock:
            for i, note in enumerate(cls._notes):
                if note["id"] == note_id:
                    del cls._notes[i]
                    return {"message": f"Note with ID {note_id} deleted successfully"}
            # Not found
            raise KeyError(f"Note with ID {note_id} not found")