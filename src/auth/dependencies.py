from datetime import datetime

from fastapi import Header, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.auth.jwt import decode_token
from src.db.client import get_db
from src.utils.validators import hash_value

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Security(security),
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
) -> dict:
    if credentials is None and not x_api_key:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing credentials")

    with get_db() as db:
        if credentials is not None:
            try:
                payload = decode_token(credentials.credentials)
            except ValueError as exc:
                raise HTTPException(status_code=401, detail="Invalid token") from exc
            if payload.get("type") != "access":
                raise HTTPException(status_code=401, detail="Invalid token type")
            row = db.execute("SELECT id, email FROM users WHERE id = ?", (payload.get("sub"),)).fetchone()
            if not row:
                raise HTTPException(status_code=401, detail="User not found")
            return dict(row)

        key_hash = hash_value(x_api_key)
        row = db.execute(
            "SELECT user_id, expires_at, is_active FROM api_keys WHERE key_hash = ?",
            (key_hash,),
        ).fetchone()
        if not row or row["is_active"] == 0:
            raise HTTPException(status_code=401, detail="Invalid API key")
        if row["expires_at"] and row["expires_at"] < datetime.utcnow().isoformat():
            raise HTTPException(status_code=401, detail="API key expired")
        user = db.execute("SELECT id, email FROM users WHERE id = ?", (row["user_id"],)).fetchone()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        db.execute("UPDATE api_keys SET last_used_at = CURRENT_TIMESTAMP WHERE key_hash = ?", (key_hash,))
        db.commit()
        return dict(user)
