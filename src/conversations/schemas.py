from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ConversationCreateRequest(BaseModel):
    title: str = Field(default="New conversation", max_length=500)
    model: str = Field(default="llama-3.1-8b-instant", max_length=100)
    system_prompt: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ConversationUpdateRequest(BaseModel):
    title: str | None = Field(default=None, max_length=500)
    system_prompt: str | None = None
    is_archived: bool | None = None


class ConversationResponse(BaseModel):
    id: str
    title: str
    model: str
    system_prompt: str | None
    metadata: dict[str, Any]
    is_archived: bool
    created_at: datetime
    updated_at: datetime | None


class ConversationListResponse(BaseModel):
    items: list[ConversationResponse]
    page: int
    page_size: int
    total: int
