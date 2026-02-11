
def build_context_window(messages: list[dict], max_messages: int = 20) -> list[dict]:
    return messages[-max_messages:]
