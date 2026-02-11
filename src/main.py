import uvicorn
from fastapi import FastAPI, Depends, Request
from fastapi.responses import StreamingResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# These imports assume you have your folder structure set up
from src.auth.dependencies import get_current_user
from src.messages.streaming import stream_generator

# 1. Initialize FastAPI with Redoc metadata
app = FastAPI(
    title="AI Conversation API",
    version="1.0.0",
    description="Secure REST API with SSE Streaming and Supabase Auth",
    docs_url="/docs",   # Swagger UI
    redoc_url="/redoc"  # ReDoc UI
)

# 2. Initialize Rate Limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 3. Add CORS Middleware (Essential for API accessibility)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Root Redirect: This allows you to open http://127.0.0.1:8000 
# and go directly to the ReDoc link you requested.
@app.get("/", include_in_schema=False)
async def root_to_docs():
    """Redirects base URL to ReDoc documentation."""
    return RedirectResponse(url="/redoc")

@app.get("/health", tags=["System"])
def health_check():
    return {"status": "online", "docs": "/redoc"}

@app.post(
    "/api/v1/conversations/{id}/messages/stream", 
    tags=["Messages"],
    summary="Stream AI Chat Response"
)
@limiter.limit("10/minute")
async def chat_stream(id: str, request: Request, user=Depends(get_current_user)):
    # In your full implementation, you would fetch history from Supabase here
    dummy_messages = [{"role": "user", "content": "Hello!"}]
    
    return StreamingResponse(
        stream_generator(dummy_messages, "llama3-8b-8192", id),
        media_type="text/event-stream"
    )

# 5. Entry Point
if __name__ == "__main__":
    # Runs on 127.0.0.1 (Localhost). 
    # Open http://127.0.0.1:8000 in your browser to see ReDoc.
    uvicorn.run("src.main:app", host="127.0.0.1", port=8000, reload=True)