from __future__ import annotations

import json
import time
import uuid

from src.db.client import get_db
from src.llm.client import llm_client
from src.llm.context import build_context_window
from src.llm.prompts import build_system_prompt
from src.llm.token_counter import approximate_tokens
from src.utils.cost_tracker import estimate_cost


def get_messages(conversation_id: str) -> list[dict]:
    with get_db() as db:
        rows = db.execute(
            "SELECT * FROM messages WHERE conversation_id = ? ORDER BY created_at ASC", (conversation_id,)
        ).fetchall()
        return [dict(r) for r in rows]


def create_user_message(conversation_id: str, content: str) -> None:
    with get_db() as db:
        db.execute(
            "INSERT INTO messages (id, conversation_id, role, content, token_count, metadata) VALUES (?, ?, 'user', ?, ?, '{}')",
            (str(uuid.uuid4()), conversation_id, content, approximate_tokens(content)),
        )
        db.commit()


def generate_title_if_needed(conversation: dict, content: str) -> None:
    if conversation["title"] != "New conversation":
        return
    with get_db() as db:
        db.execute(
            "UPDATE conversations SET title = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (" ".join(content.strip().split()[:8])[:80] or "Untitled", conversation["id"]),
        )
        db.commit()


def build_llm_messages(conversation: dict, message_history: list[dict], thinking: bool = False) -> list[dict]:
    system_prompt = build_system_prompt(conversation.get("system_prompt"))
    if thinking:
        system_prompt += "\nProvide brief reasoning bullets before the final answer."
    window = build_context_window(message_history)
    llm_messages = [{"role": "system", "content": system_prompt}]
    llm_messages.extend({"role": m["role"], "content": m["content"]} for m in window if m["role"] in {"user", "assistant", "system"})
    return llm_messages


async def generate_assistant_response(model: str, llm_messages: list[dict]) -> tuple[str, int]:
    start = time.perf_counter()
    chunks = []
    async for token in llm_client.stream_completion(llm_messages, model):
        chunks.append(token)
    latency_ms = int((time.perf_counter() - start) * 1000)
    return "".join(chunks).strip(), latency_ms


def save_assistant_message(conversation_id: str, content: str, model: str, latency_ms: int) -> dict:
    output_tokens = approximate_tokens(content)
    message_id = str(uuid.uuid4())
    with get_db() as db:
        db.execute(
            """
            INSERT INTO messages (id, conversation_id, role, content, token_count, model, finish_reason, latency_ms, metadata, estimated_cost_usd)
            VALUES (?, ?, 'assistant', ?, ?, ?, 'stop', ?, ?, ?)
            """,
            (
                message_id,
                conversation_id,
                content,
                output_tokens,
                model,
                latency_ms,
                json.dumps({"usage": {"output_tokens": output_tokens}}),
                estimate_cost(model, 0, output_tokens),
            ),
        )
        db.commit()
        row = db.execute("SELECT * FROM messages WHERE id = ?", (message_id,)).fetchone()
        return dict(row)
