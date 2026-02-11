from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config.settings import Settings


def setup_cors(app: FastAPI, settings: Settings) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID", "Retry-After"],
    )
