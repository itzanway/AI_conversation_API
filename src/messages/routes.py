from __future__ import annotations

import json
import uuid

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import StreamingResponse

from src.conversations import repository
from src.conversations.service import ensure_owner
from src.llm.client import llm_client
from src.llm.token_counter import approximate_tokens
from src.messages.schemas import MessageCreateRequest, MessageListResponse, MessageResponse
from src.messages.service import (
    build_llm_messages,
    create_user_message,
    generate_assistant_response,
    generate_title_if_needed,
    get_messages,
    save_assistant_message,
)
from src.messages.streaming import sse_event
from src.middleware.dependencies import generation_rate_limit, standard_rate_limit

router = APIRouter(prefix="/conversations/{conversation_id}", tags=["Messages", "Streaming"])


def to_response(message: dict) -> MessageResponse:
    return MessageResponse(
        id=message["id"],
        role=message["role"],
        content=message["content"],
        token_count=message["token_count"],
        model=message["model"],
        finish_reason=message["finish_reason"],
        latency_ms=message["latency_ms"],
        metadata=json.loads(message.get("metadata") or "{}"),
        created_at=message["created_at"],
    )


@router.get("/messages", response_model=MessageListResponse, summary="List messages")
async def list_messages(
    conversation_id: str,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    user: dict = Depends(standard_rate_limit),
) -> MessageListResponse:
    conversation = ensure_owner(repository.get_conversation(conversation_id), user)
    all_messages = get_messages(conversation["id"])
    start = (page - 1) * page_size
    items = all_messages[start : start + page_size]
    return MessageListResponse(items=[to_response(m) for m in items], page=page, page_size=page_size, total=len(all_messages))


@router.post("/messages", response_model=MessageResponse, summary="Send message (non-stream)")
async def create_message(
    conversation_id: str,
    payload: MessageCreateRequest,
    user: dict = Depends(generation_rate_limit),
) -> MessageResponse:
    conversation = ensure_owner(repository.get_conversation(conversation_id), user)
    create_user_message(conversation["id"], payload.content)
    generate_title_if_needed(conversation, payload.content)

    history = get_messages(conversation["id"])
    llm_messages = build_llm_messages(conversation, history, payload.thinking)
    model = payload.model or conversation["model"]
    content, latency_ms = await generate_assistant_response(model, llm_messages)
    assistant = save_assistant_message(conversation["id"], content, model, latency_ms)
    return to_response(assistant)


@router.post("/messages/stream", summary="Send message (SSE stream)")
async def stream_message(
    conversation_id: str,
    payload: MessageCreateRequest,
    request: Request,
    user: dict = Depends(generation_rate_limit),
) -> StreamingResponse:
    conversation = ensure_owner(repository.get_conversation(conversation_id), user)
    create_user_message(conversation["id"], payload.content)
    generate_title_if_needed(conversation, payload.content)
    history = get_messages(conversation["id"])
    llm_messages = build_llm_messages(conversation, history, payload.thinking)
    model = payload.model or conversation["model"]

    async def event_stream():
        message_id = f"msg_{uuid.uuid4().hex[:12]}"
        full_text = ""
        yield sse_event("message_start", {"type": "message_start", "message": {"id": message_id, "role": "assistant", "model": model}})
        yield sse_event("content_block_start", {"type": "content_block_start", "index": 0, "content_block": {"type": "text", "text": ""}})
        try:
            async for token in llm_client.stream_completion(llm_messages, model):
                if await request.is_disconnected():
                    break
                full_text += token
                yield sse_event("content_block_delta", {"type": "content_block_delta", "index": 0, "delta": {"type": "text_delta", "text": token}})
            yield sse_event("content_block_stop", {"type": "content_block_stop", "index": 0})
            yield sse_event("message_delta", {"type": "message_delta", "delta": {"stop_reason": "end_turn"}, "usage": {"output_tokens": approximate_tokens(full_text)}})
            yield sse_event("message_stop", {"type": "message_stop"})
            if full_text.strip():
                save_assistant_message(conversation["id"], full_text.strip(), model, latency_ms=0)
        except Exception as exc:
            yield sse_event("error", {"type": "error", "error": {"type": "generation_error", "message": str(exc)}})

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.get("/events", summary="Conversation event stream")
async def conversation_events(conversation_id: str, request: Request, user: dict = Depends(standard_rate_limit)) -> StreamingResponse:
    ensure_owner(repository.get_conversation(conversation_id), user)

    async def event_stream():
        yield sse_event("heartbeat", {"type": "heartbeat", "conversation_id": conversation_id})
        while not await request.is_disconnected():
            break

    return StreamingResponse(event_stream(), media_type="text/event-stream")
