from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    roberta_loaded: bool
    mistral_available: bool | None = None
    error: str | None = None
