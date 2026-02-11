from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator

from groq import AsyncGroq

from src.config.settings import get_settings

settings = get_settings()


class LLMClient:
    def __init__(self) -> None:
        self._client = AsyncGroq(api_key=settings.groq_api_key) if settings.groq_api_key else None

    async def stream_completion(self, messages: list[dict], model: str) -> AsyncIterator[str]:
        if not self._client:
            fallback = f"Simulated response for: {messages[-1]['content']}"
            for token in fallback.split(" "):
                await asyncio.sleep(0.01)
                yield token + " "
            return

        stream = await self._client.chat.completions.create(messages=messages, model=model, stream=True)
        async for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            if delta:
                yield delta


llm_client = LLMClient()
