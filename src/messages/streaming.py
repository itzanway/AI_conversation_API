import json


def sse_event(event_type: str, payload: dict) -> str:
    return f"event: {event_type}\ndata: {json.dumps(payload)}\n\n"
