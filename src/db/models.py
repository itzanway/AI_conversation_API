from typing import TypedDict


class User(TypedDict):
    id: str
    email: str


class Conversation(TypedDict):
    id: str
    user_id: str
    title: str
    model: str
    system_prompt: str | None
    metadata: str
    is_archived: int
    is_deleted: int
    created_at: str
    updated_at: str
