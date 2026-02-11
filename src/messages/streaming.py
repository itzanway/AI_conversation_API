import json
from groq import AsyncGroq
import os

client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

async def stream_generator(messages, model, conversation_id):
    # 1. Start Message
    yield f"event: message_start\ndata: {json.dumps({'type': 'message_start', 'message': {'role': 'assistant', 'model': model}})}\n\n"
    
    full_response = ""
    stream = await client.chat.completions.create(
        messages=messages,
        model=model,
        stream=True
    )

    yield f"event: content_block_start\ndata: {json.dumps({'index': 0})}\n\n"

    async for chunk in stream:
        delta = chunk.choices[0].delta.content or ""
        if delta:
            full_response += delta
            yield f"event: content_block_delta\ndata: {json.dumps({'delta': {'text': delta}})}\n\n"

    yield f"event: content_block_stop\ndata: {json.dumps({'index': 0})}\n\n"
    yield f"event: message_stop\ndata: {json.dumps({})}\n\n"
    
    # 📝 TODO: Insert full_response into Supabase messages table here