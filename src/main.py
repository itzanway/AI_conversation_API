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
