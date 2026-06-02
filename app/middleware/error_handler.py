import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions import AppError

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def app_error_handler(_: Request, exc: AppError) -> JSONResponse:
        if exc.status_code >= 500:
            logger.error(exc.message)
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status": "error",
                "service": exc.service,
                "message": exc.message,
            },
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled application error")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "service": "middleware",
                "message": "Unexpected internal error",
            },
        )

