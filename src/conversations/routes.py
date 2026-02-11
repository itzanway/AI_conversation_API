import json

from fastapi import APIRouter, Depends, Query

from src.conversations import repository, service
from src.conversations.schemas import (
    ConversationCreateRequest,
    ConversationListResponse,
    ConversationResponse,
    ConversationUpdateRequest,
)
from src.middleware.dependencies import standard_rate_limit

router = APIRouter(prefix="/conversations", tags=["Conversations"])


def to_response(conversation: dict) -> ConversationResponse:
    return ConversationResponse(
        id=conversation["id"],
        title=conversation["title"],
        model=conversation["model"],
        system_prompt=conversation["system_prompt"],
        metadata=json.loads(conversation.get("metadata") or "{}"),
        is_archived=bool(conversation["is_archived"]),
        created_at=conversation["created_at"],
        updated_at=conversation["updated_at"],
    )


@router.post("", response_model=ConversationResponse, summary="Create conversation")
async def create_conversation(payload: ConversationCreateRequest, user: dict = Depends(standard_rate_limit)) -> ConversationResponse:
    conversation = repository.create_conversation(
        user["id"],
        {"title": payload.title, "model": payload.model, "system_prompt": payload.system_prompt, "metadata": payload.metadata},
    )
    return to_response(conversation)


@router.get("", response_model=ConversationListResponse, summary="List conversations")
async def list_user_conversations(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    user: dict = Depends(standard_rate_limit),
) -> ConversationListResponse:
    items, total = repository.list_conversations(user["id"], page, page_size)
    return ConversationListResponse(items=[to_response(x) for x in items], page=page, page_size=page_size, total=total)


@router.get("/{conversation_id}", response_model=ConversationResponse, summary="Get conversation")
async def get_one_conversation(conversation_id: str, user: dict = Depends(standard_rate_limit)) -> ConversationResponse:
    conversation = service.ensure_owner(repository.get_conversation(conversation_id), user)
    return to_response(conversation)


@router.patch("/{conversation_id}", response_model=ConversationResponse, summary="Update conversation")
async def update_one_conversation(
    conversation_id: str,
    payload: ConversationUpdateRequest,
    user: dict = Depends(standard_rate_limit),
) -> ConversationResponse:
    service.ensure_owner(repository.get_conversation(conversation_id), user)
    updates = payload.model_dump(exclude_none=True)
    updated = service.update_conversation(conversation_id, updates)
    return to_response(updated)


@router.delete("/{conversation_id}", summary="Delete conversation")
async def delete_one_conversation(
    conversation_id: str,
    hard_delete: bool = Query(default=False),
    user: dict = Depends(standard_rate_limit),
) -> dict[str, str]:
    service.ensure_owner(repository.get_conversation(conversation_id), user)
    service.delete_conversation(conversation_id, hard_delete)
    return {"message": "Deleted"}
