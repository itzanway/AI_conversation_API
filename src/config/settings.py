import json
import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass
class Settings:
    app_name: str
    api_prefix: str
    environment: str
    debug: bool
    database_path: str
    jwt_secret: str
    access_token_exp_minutes: int
    refresh_token_exp_minutes: int
    cors_allowed_origins: list[str]
    primary_model: str
    fallback_model: str
    groq_api_key: str | None
    default_system_prompt: str


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    origins = os.getenv("CORS_ALLOWED_ORIGINS", '["http://localhost:3000"]')
    try:
        parsed_origins = json.loads(origins)
    except json.JSONDecodeError:
        parsed_origins = ["http://localhost:3000"]
    return Settings(
        app_name=os.getenv("APP_NAME", "AI Conversation API"),
        api_prefix=os.getenv("API_PREFIX", "/api/v1"),
        environment=os.getenv("ENVIRONMENT", "development"),
        debug=os.getenv("DEBUG", "false").lower() == "true",
        database_path=os.getenv("DATABASE_PATH", "conversation.db"),
        jwt_secret=os.getenv("JWT_SECRET", "change-me"),
        access_token_exp_minutes=int(os.getenv("ACCESS_TOKEN_EXP_MINUTES", "30")),
        refresh_token_exp_minutes=int(os.getenv("REFRESH_TOKEN_EXP_MINUTES", str(60 * 24 * 7))),
        cors_allowed_origins=parsed_origins,
        primary_model=os.getenv("PRIMARY_MODEL", "llama-3.1-8b-instant"),
        fallback_model=os.getenv("FALLBACK_MODEL", "gemma2-9b-it"),
        groq_api_key=os.getenv("GROQ_API_KEY"),
        default_system_prompt=os.getenv(
            "DEFAULT_SYSTEM_PROMPT",
            "You are a helpful, concise AI assistant. Provide accurate answers and mention assumptions.",
        ),
    )
