from datetime import datetime, timedelta, timezone
from typing import Any

import jwt

from src.config.settings import get_settings

settings = get_settings()


def create_access_token(subject: str) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_exp_minutes)
    payload = {"sub": subject, "type": "access", "exp": exp}
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def create_refresh_token(subject: str) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=settings.refresh_token_exp_minutes)
    payload = {"sub": subject, "type": "refresh", "exp": exp}
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")


def decode_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
    except jwt.PyJWTError as exc:
        raise ValueError("Invalid token") from exc
