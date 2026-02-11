from fastapi import HTTPException

from src.db.client import get_db


def ensure_owner(conversation: dict | None, user: dict) -> dict:
    if not conversation or conversation.get("is_deleted"):
        raise HTTPException(status_code=404, detail="Conversation not found")
    if conversation["user_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Forbidden")
    return conversation


def update_conversation(conversation_id: str, payload: dict) -> dict:
    with get_db() as db:
        allowed = {"title", "system_prompt", "is_archived"}
        for key, value in payload.items():
            if key not in allowed:
                continue
            db.execute(f"UPDATE conversations SET {key} = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (value, conversation_id))
        db.commit()
        row = db.execute("SELECT * FROM conversations WHERE id = ?", (conversation_id,)).fetchone()
        return dict(row)


def delete_conversation(conversation_id: str, hard_delete: bool) -> None:
    with get_db() as db:
        if hard_delete:
            db.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
            db.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
        else:
            db.execute("UPDATE conversations SET is_deleted = 1 WHERE id = ?", (conversation_id,))
        db.commit()
