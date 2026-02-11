
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from src.auth import routes as auth_routes
from src.config.cors import setup_cors
from src.config.settings import get_settings
from src.conversations import routes as conversation_routes
from src.db.client import init_db
from src.messages import routes as message_routes
from src.middleware.error_handler import register_exception_handlers
from src.middleware.request_id import RequestIDMiddleware
from src.usage import routes as usage_routes

settings = get_settings()
app = FastAPI(title=settings.app_name, version="1.0.0", docs_url="/docs", redoc_url="/redoc")

app.add_middleware(RequestIDMiddleware)
setup_cors(app, settings)
register_exception_handlers(app)
init_db()


@app.middleware("http")
async def security_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response



app.include_router(auth_routes.router, prefix=settings.api_prefix)
app.include_router(conversation_routes.router, prefix=settings.api_prefix)
app.include_router(message_routes.router, prefix=settings.api_prefix)
app.include_router(usage_routes.router, prefix=settings.api_prefix)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(title=settings.app_name, version="1.0.0", routes=app.routes)
    schema.setdefault("components", {})["securitySchemes"] = {
        "BearerAuth": {"type": "http", "scheme": "bearer"},
        "ApiKeyAuth": {"type": "apiKey", "in": "header", "name": "X-API-Key"},
    }
    for _, path_item in schema.get("paths", {}).items():
        for _, operation in path_item.items():
            if "Auth" not in operation.get("tags", []):
                operation["security"] = [{"BearerAuth": []}, {"ApiKeyAuth": []}]
    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = custom_openapi
=======
from fastapi import FastAPI, Depends, Request
from fastapi.responses import StreamingResponse
from src.auth.dependencies import get_current_user
from src.messages.streaming import stream_generator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

app = FastAPI(title="AI Conversation API", version="1.0.0")
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/")
def health_check():
    return {"status": "online"}

@app.post("/api/v1/conversations/{id}/messages/stream")
@limiter.limit("10/minute")
async def chat_stream(id: str, request: Request, user=Depends(get_current_user)):
    # In a real app, you'd fetch message history from DB here
    dummy_messages = [{"role": "user", "content": "Hello!"}]
    
    return StreamingResponse(
        stream_generator(dummy_messages, "llama3-8b-8192", id),
        media_type="text/event-stream"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
