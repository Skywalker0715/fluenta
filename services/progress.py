from contextlib import closing

import db


def get_stats() -> dict:
    with closing(db.get_connection()) as conn:
        sessions = conn.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
        user_messages = conn.execute(
            "SELECT COUNT(*) FROM messages WHERE role = 'user'"
        ).fetchone()[0]
        corrections = conn.execute(
            "SELECT COUNT(*) FROM messages WHERE correction IS NOT NULL"
        ).fetchone()[0]
    return {
        "sessions": sessions,
        "user_messages": user_messages,
        "corrections": corrections,
    }


def recent_corrections(limit: int = 20) -> list[dict]:
    with closing(db.get_connection()) as conn:
        rows = conn.execute(
            """
            SELECT m.correction AS correction, m.created_at AS created_at,
                   (
                       SELECT u.text
                       FROM messages u
                       WHERE u.session_id = m.session_id
                         AND u.role = 'user'
                         AND u.id < m.id
                       ORDER BY u.id DESC
                       LIMIT 1
                   ) AS original
            FROM messages m
            WHERE m.correction IS NOT NULL
            ORDER BY m.id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [
        {
            "original": row["original"],
            "correction": row["correction"],
            "created_at": row["created_at"],
        }
        for row in rows
    ]


def corrections_per_day(days: int = 14) -> list[dict]:
    with closing(db.get_connection()) as conn:
        rows = conn.execute(
            """
            SELECT date(created_at) AS day, COUNT(*) AS count
            FROM messages
            WHERE correction IS NOT NULL
              AND created_at >= datetime('now', ?)
            GROUP BY day
            ORDER BY day
            """,
            (f"-{days} days",),
        ).fetchall()
    return [{"day": row["day"], "count": row["count"]} for row in rows]
