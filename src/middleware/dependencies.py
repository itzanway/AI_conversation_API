from fastapi import Depends

from src.auth.dependencies import get_current_user
from src.middleware.rate_limiter import rate_limiter


async def standard_rate_limit(user: dict = Depends(get_current_user)) -> dict:
    rate_limiter.check(f"std:{user['id']}", limit=60)
    return user


async def generation_rate_limit(user: dict = Depends(get_current_user)) -> dict:
    rate_limiter.check(f"gen:{user['id']}", limit=10)
    return user
