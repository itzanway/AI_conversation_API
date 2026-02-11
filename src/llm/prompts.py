from src.config.settings import get_settings


def build_system_prompt(custom_system_prompt: str | None) -> str:
    settings = get_settings()
    return custom_system_prompt or settings.default_system_prompt
