import datetime
import difflib

import db
from services.fixparse import parse_fix


def _today() -> str:
    return datetime.date.today().isoformat()


def _init_table() -> None:
    with db.get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS drills (
                message_id INTEGER PRIMARY KEY,
                box INTEGER NOT NULL DEFAULT 1,
                due TEXT NOT NULL,
                last_result TEXT
            )
            """
        )


def sync() -> int:
    _init_table()
    today = _today()
    tambah = 0
    with db.get_connection() as conn:
        existing = {
            row["message_id"]
            for row in conn.execute("SELECT message_id FROM drills").fetchall()
        }
        rows = conn.execute(
            """
            SELECT m.id, m.correction
            FROM messages m
            WHERE m.role = 'ai' AND m.correction IS NOT NULL
            """
        ).fetchall()
        for row in rows:
            if row["id"] in existing:
                continue
            hasil = parse_fix(row["correction"])
            if not hasil["structured"]:
                continue
            conn.execute(
                "INSERT INTO drills (message_id, box, due, last_result) VALUES (?, 1, ?, NULL)",
                (row["id"], today),
            )
            tambah += 1
    return tambah


def next_items(limit: int = 5) -> list[dict]:
    _init_table()
    today = _today()
    with db.get_connection() as conn:
        rows = conn.execute(
            """
            SELECT d.message_id, d.box,
                   m.correction,
                   (SELECT u.text
                    FROM messages u
                    WHERE u.session_id = m.session_id
                      AND u.role = 'user'
                      AND u.id < m.id
                    ORDER BY u.id DESC
                    LIMIT 1) AS original
            FROM drills d
            JOIN messages m ON m.id = d.message_id
            WHERE d.due <= ?
            ORDER BY d.due ASC, d.box ASC
            LIMIT ?
            """,
            (today, limit),
        ).fetchall()
    result = []
    for row in rows:
        hasil = parse_fix(row["correction"])
        result.append(
            {
                "message_id": row["message_id"],
                "original": row["original"],
                "corrected": hasil["corrected"],
                "explanation": hasil["explanation"],
                "tag": hasil["tag"],
                "box": row["box"],
            }
        )
    return result


def _normalize(teks: str) -> str:
    teks = teks.lower().strip()
    teks = " ".join(teks.split())
    return teks.rstrip(".,!?;:")


def grade(answer: str, corrected: str) -> str:
    a = _normalize(answer)
    b = _normalize(corrected)
    if a == b:
        return "benar"
    ratio = difflib.SequenceMatcher(None, a, b).ratio()
    if ratio >= 0.85:
        return "hampir"
    return "salah"


_INTERVALS = {1: 1, 2: 2, 3: 4, 4: 8, 5: 16}


def record(message_id: int, result: str) -> None:
    _init_table()
    today = datetime.date.today()
    with db.get_connection() as conn:
        row = conn.execute(
            "SELECT box FROM drills WHERE message_id = ?", (message_id,)
        ).fetchone()
        if row is None:
            return
        box = row["box"]
        if result == "benar":
            box = min(box + 1, 5)
            due = today + datetime.timedelta(days=_INTERVALS[box])
        elif result == "hampir":
            due = today + datetime.timedelta(days=1)
        else:
            box = 1
            due = today + datetime.timedelta(days=1)
        conn.execute(
            "UPDATE drills SET box = ?, due = ?, last_result = ? WHERE message_id = ?",
            (box, due.isoformat(), result, message_id),
        )


def stats() -> dict:
    _init_table()
    today = _today()
    with db.get_connection() as conn:
        total = conn.execute("SELECT COUNT(*) FROM drills").fetchone()[0]
        due = conn.execute(
            "SELECT COUNT(*) FROM drills WHERE due <= ?", (today,)
        ).fetchone()[0]
        mastered = conn.execute(
            "SELECT COUNT(*) FROM drills WHERE box >= 4"
        ).fetchone()[0]
    return {"total": total, "due": due, "mastered": mastered}
