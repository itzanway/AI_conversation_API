# AI Conversation API (FastAPI)

Production-oriented REST + SSE API for AI-powered conversations.

## Features
- JWT auth (`/register`, `/login`, `/refresh`, `/logout`)
- Conversation CRUD with ownership authorization
- Message creation (sync + SSE streaming)
- SSE event format compatible with Claude/OpenAI-like event flow
- In-memory per-user rate limiting (60 RPM standard, 10 RPM generation)
- Request ID headers (`X-Request-ID`) and security headers
- Token counting + estimated cost tracking
- Auto title generation on first user message
- OpenAPI docs at `/docs` and `/redoc`

## Quickstart
1. Create and activate venv
2. Install deps: `pip install -r requirements.txt`
3. Copy env: `cp .env.example .env`
4. Run API: `uvicorn src.main:app --reload`

## Auth
Use one of:
- `Authorization: Bearer <access_token>`
- `X-API-Key: <raw_api_key>`

## Endpoints
- Auth: `/api/v1/auth/*`
- Conversations: `/api/v1/conversations`
- Messages: `/api/v1/conversations/{id}/messages`
- Streaming: `/api/v1/conversations/{id}/messages/stream`, `/api/v1/conversations/{id}/events`
- Usage: `/api/v1/usage/stats`, `/api/v1/models`

## Notes
- Default DB URL points to local SQLite for easy startup; set PostgreSQL/Supabase URL in production.
- For Supabase RLS, mirror the schema in `database/schema.sql` and enforce policies by `auth.uid() = user_id`.
