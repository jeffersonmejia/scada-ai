from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.api.routes_chat import router as chat_router
from app.api.routes_chat import web_router
from app.api.routes_health import router as health_router
from app.core.config import Settings
from app.core.logging import configure_logging
from app.middleware.error_handler import register_exception_handlers


def create_app() -> FastAPI:
    settings = Settings()
    configure_logging(settings.log_level)

    app = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        description="Security middleware for SCADA and electrical-grid LLM requests.",
    )
    app.state.settings = settings

    register_exception_handlers(app)
    app.include_router(health_router)
    app.include_router(chat_router)
    app.include_router(web_router)
    app.mount("/", StaticFiles(directory="app/web", html=True), name="web")

    return app
