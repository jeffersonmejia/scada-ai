from fastapi import Depends, Header

from app.api.deps import get_settings
from app.core.config import Settings
from app.core.exceptions import UnauthorizedError


async def require_api_key(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    settings: Settings = Depends(get_settings),
) -> None:
    expected = settings.api_key.get_secret_value()
    if not x_api_key or x_api_key != expected:
        raise UnauthorizedError(message="Invalid or missing API key", service="middleware")

