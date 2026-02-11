# Architecture

## Layers
- **Routes**: request/response handling + validation via Pydantic.
- **Service**: orchestration (context window, title generation, streaming persistence).
- **Repository**: DB query encapsulation for conversations.
- **LLM abstraction**: `src/llm/client.py` supports Groq streaming + local fallback.

## Security
- JWT and API key auth in `src/auth/dependencies.py`.
- Ownership checks via `ensure_owner`.
- Per-user rate limiting in `src/middleware/rate_limiter.py`.
- Structured generic 500 responses in `src/middleware/error_handler.py`.
- Request IDs and security headers in `src/main.py`.

## Streaming
SSE stream emits:
1. `message_start`
2. `content_block_start`
3. repeated `content_block_delta`
4. `content_block_stop`
5. `message_delta`
6. `message_stop`
7. optional `error`

## Cost and token tracking
- Approx token counting in `src/llm/token_counter.py`
- Estimated cost in `src/utils/cost_tracker.py`
- Saved on assistant messages.
