"""Сховище нотаток на SQLite (стандартна бібліотека, без зовнішніх залежностей).

Файл БД задається через DATABASE_PATH — у Docker його варто
винести у volume, щоб дані не зникали при перезапуску контейнера.
"""

import sqlite3
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path

from app.models import Note, NoteCreate, NoteReplace, NoteUpdate

SCHEMA = """
CREATE TABLE IF NOT EXISTS notes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT NOT NULL,
    content     TEXT NOT NULL DEFAULT '',
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);
"""


class NoteStorage:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        if db_path != ":memory:":
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.executescript(SCHEMA)

    @contextmanager
    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    @staticmethod
    def _row_to_note(row: sqlite3.Row) -> Note:
        return Note(
            id=row["id"],
            title=row["title"],
            content=row["content"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def ping(self) -> bool:
        try:
            with self._connect() as conn:
                conn.execute("SELECT 1")
            return True
        except sqlite3.Error:
            return False

    def list(self, search: str | None = None, limit: int = 50, offset: int = 0) -> list[Note]:
        query = "SELECT * FROM notes"
        params: list = []
        if search:
            query += " WHERE title LIKE ? OR content LIKE ?"
            params += [f"%{search}%", f"%{search}%"]
        query += " ORDER BY id DESC LIMIT ? OFFSET ?"
        params += [limit, offset]
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [self._row_to_note(r) for r in rows]

    def get(self, note_id: int) -> Note | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
        return self._row_to_note(row) if row else None

    def create(self, data: NoteCreate) -> Note:
        now = datetime.now(UTC).isoformat()
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO notes (title, content, created_at, updated_at) VALUES (?, ?, ?, ?)",
                (data.title, data.content, now, now),
            )
            note_id = cur.lastrowid
        return self.get(note_id)  # type: ignore[return-value]

    def replace(self, note_id: int, data: NoteReplace) -> Note | None:
        """PUT: повністю замінює вміст нотатки."""
        return self._write(note_id, data.title, data.content)

    def update(self, note_id: int, data: NoteUpdate) -> Note | None:
        """PATCH: змінює лише передані поля."""
        existing = self.get(note_id)
        if existing is None:
            return None
        title = data.title if data.title is not None else existing.title
        content = data.content if data.content is not None else existing.content
        return self._write(note_id, title, content)

    def _write(self, note_id: int, title: str, content: str) -> Note | None:
        if self.get(note_id) is None:
            return None
        now = datetime.now(UTC).isoformat()
        with self._connect() as conn:
            conn.execute(
                "UPDATE notes SET title = ?, content = ?, updated_at = ? WHERE id = ?",
                (title, content, now, note_id),
            )
        return self.get(note_id)

    def delete(self, note_id: int) -> bool:
        with self._connect() as conn:
            cur = conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        return cur.rowcount > 0
