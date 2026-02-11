from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class MessageCreateRequest(BaseModel):
    content: str = Field(min_length=1, max_length=20000)
    model: str | None = None
    thinking: bool = False


class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    token_count: int
    model: str | None
    finish_reason: str | None
    latency_ms: int | None
    metadata: dict[str, Any]
    created_at: datetime


class MessageListResponse(BaseModel):
    items: list[MessageResponse]
    page: int
    page_size: int
    total: int
