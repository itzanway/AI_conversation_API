import json
import uuid

from src.db.client import get_db


def create_conversation(user_id: str, payload: dict) -> dict:
    conversation_id = str(uuid.uuid4())
    with get_db() as db:
        db.execute(
            """
            INSERT INTO conversations (id, user_id, title, model, system_prompt, metadata, is_archived, is_deleted)
            VALUES (?, ?, ?, ?, ?, ?, 0, 0)
            """,
            (
                conversation_id,
                user_id,
                payload["title"],
                payload["model"],
                payload.get("system_prompt"),
                json.dumps(payload.get("metadata", {})),
            ),
        )
        db.commit()
        row = db.execute("SELECT * FROM conversations WHERE id = ?", (conversation_id,)).fetchone()
        return dict(row)


def list_conversations(user_id: str, page: int, page_size: int) -> tuple[list[dict], int]:
    with get_db() as db:
        total = db.execute(
            "SELECT COUNT(*) as c FROM conversations WHERE user_id = ? AND is_deleted = 0", (user_id,)
        ).fetchone()["c"]
        rows = db.execute(
            """
            SELECT * FROM conversations
            WHERE user_id = ? AND is_deleted = 0
            ORDER BY updated_at DESC
            LIMIT ? OFFSET ?
            """,
            (user_id, page_size, (page - 1) * page_size),
        ).fetchall()
        return [dict(r) for r in rows], int(total)


def get_conversation(conversation_id: str) -> dict | None:
    with get_db() as db:
        row = db.execute("SELECT * FROM conversations WHERE id = ?", (conversation_id,)).fetchone()
        return dict(row) if row else None
