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