import time
from collections import defaultdict, deque

from fastapi import HTTPException


class InMemoryRateLimiter:
    def __init__(self) -> None:
        self._store: dict[str, deque[float]] = defaultdict(deque)

    def check(self, key: str, limit: int, window_seconds: int = 60) -> None:
        now = time.time()
        q = self._store[key]
        while q and q[0] < now - window_seconds:
            q.popleft()
        if len(q) >= limit:
            retry_after = int(window_seconds - (now - q[0])) + 1
            raise HTTPException(status_code=429, detail="Rate limit exceeded", headers={"Retry-After": str(retry_after)})
        q.append(now)


rate_limiter = InMemoryRateLimiter()
