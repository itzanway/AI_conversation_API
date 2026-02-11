from fastapi import APIRouter, Depends

from src.config.settings import get_settings
from src.db.client import get_db
from src.middleware.dependencies import standard_rate_limit

router = APIRouter(tags=["Usage"])
settings = get_settings()


@router.get("/usage/stats", summary="Get usage stats")
async def usage_stats(user: dict = Depends(standard_rate_limit)) -> dict:
    with get_db() as db:
        row = db.execute(
            """
            SELECT COUNT(messages.id) as message_count,
                   COALESCE(SUM(messages.token_count), 0) as token_count,
                   COALESCE(SUM(messages.estimated_cost_usd), 0) as estimated_cost
            FROM messages
            JOIN conversations ON conversations.id = messages.conversation_id
            WHERE conversations.user_id = ?
            """,
            (user["id"],),
        ).fetchone()
    return {"messages": int(row["message_count"]), "tokens": int(row["token_count"]), "estimated_cost_usd": float(row["estimated_cost"])}


@router.get("/models", summary="List available models")
async def list_models() -> dict:
    return {
        "primary": settings.primary_model,
        "fallback": settings.fallback_model,
        "available": [settings.primary_model, settings.fallback_model],
    }
