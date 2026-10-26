import os
import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "app.db"
SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('user', 'ai')),
    text TEXT NOT NULL,
    correction TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (session_id) REFERENCES sessions (id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    task TEXT NOT NULL,
    result_text TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
"""


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_connection() as conn:
        conn.executescript(SCHEMA)
        
def create_session(title: str = "New chat") -> int:
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO sessions (title) VALUES (?)", (title,)
        )
        return cur.lastrowid


def list_sessions() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, title, created_at FROM sessions ORDER BY id DESC"
        ).fetchall()
    return [dict(row) for row in rows]


def add_message(
    session_id: int, role: str, text: str, correction: str | None = None
) -> None:
    if role not in ("user", "ai"):
        raise ValueError("role must be 'user' or 'ai'")
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO messages (session_id, role, text, correction) VALUES (?, ?, ?, ?)",
            (session_id, role, text, correction),
        )


def get_messages(session_id: int) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT role, text, correction FROM messages WHERE session_id = ? ORDER BY id ASC",
            (session_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def save_document(filename: str, task: str, result_text: str) -> int:
    with get_connection() as conn:
        cur = conn.execute(
            "INSERT INTO documents (filename, task, result_text) VALUES (?, ?, ?)",
            (filename, task, result_text),
        )
        return cur.lastrowid

def delete_session(session_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM sessions WHERE id = ?", (session_id,))