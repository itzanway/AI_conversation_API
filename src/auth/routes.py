from datetime import datetime, timedelta
import uuid

from fastapi import APIRouter, HTTPException, status

from src.auth.jwt import create_access_token, create_refresh_token, decode_token
from src.auth.schemas import LoginRequest, LogoutRequest, RefreshRequest, RegisterRequest, TokenResponse
from src.db.client import get_db
from src.utils.validators import hash_password, hash_value, verify_password

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=TokenResponse, summary="Register user")
async def register(payload: RegisterRequest) -> TokenResponse:
    with get_db() as db:
        existing = db.execute("SELECT id FROM users WHERE email = ?", (payload.email,)).fetchone()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        user_id = str(uuid.uuid4())
        db.execute(
            "INSERT INTO users (id, email, password_hash) VALUES (?, ?, ?)",
            (user_id, payload.email, hash_password(payload.password)),
        )

        access_token = create_access_token(user_id)
        refresh_token = create_refresh_token(user_id)
        db.execute(
            "INSERT INTO refresh_tokens (id, user_id, token_hash, expires_at, revoked) VALUES (?, ?, ?, ?, 0)",
            (
                str(uuid.uuid4()),
                user_id,
                hash_value(refresh_token),
                (datetime.utcnow() + timedelta(days=7)).isoformat(),
            ),
        )
        db.commit()
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/login", response_model=TokenResponse, summary="Login user")
async def login(payload: LoginRequest) -> TokenResponse:
    with get_db() as db:
        user = db.execute("SELECT id, password_hash FROM users WHERE email = ?", (payload.email,)).fetchone()
        if not user or not verify_password(payload.password, user["password_hash"]):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

        access_token = create_access_token(user["id"])
        refresh_token = create_refresh_token(user["id"])
        db.execute(
            "INSERT INTO refresh_tokens (id, user_id, token_hash, expires_at, revoked) VALUES (?, ?, ?, ?, 0)",
            (
                str(uuid.uuid4()),
                user["id"],
                hash_value(refresh_token),
                (datetime.utcnow() + timedelta(days=7)).isoformat(),
            ),
        )
        db.commit()
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse, summary="Refresh access token")
async def refresh(payload: RefreshRequest) -> TokenResponse:
    try:
        token_data = decode_token(payload.refresh_token)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail="Invalid refresh token") from exc
    if token_data.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    with get_db() as db:
        token_hash = hash_value(payload.refresh_token)
        token = db.execute(
            "SELECT id FROM refresh_tokens WHERE token_hash = ? AND revoked = 0",
            (token_hash,),
        ).fetchone()
        if not token:
            raise HTTPException(status_code=401, detail="Refresh token revoked")

        db.execute("UPDATE refresh_tokens SET revoked = 1 WHERE id = ?", (token["id"],))
        access_token = create_access_token(token_data["sub"])
        refresh_token = create_refresh_token(token_data["sub"])
        db.execute(
            "INSERT INTO refresh_tokens (id, user_id, token_hash, expires_at, revoked) VALUES (?, ?, ?, ?, 0)",
            (
                str(uuid.uuid4()),
                token_data["sub"],
                hash_value(refresh_token),
                (datetime.utcnow() + timedelta(days=7)).isoformat(),
            ),
        )
        db.commit()
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/logout", summary="Logout user")
async def logout(payload: LogoutRequest) -> dict[str, str]:
    with get_db() as db:
        db.execute("UPDATE refresh_tokens SET revoked = 1 WHERE token_hash = ?", (hash_value(payload.refresh_token),))
        db.commit()
    return {"message": "Logged out"}
