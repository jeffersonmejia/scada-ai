from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    classifier_loaded: bool
    qwen_available: bool | None = None
    error: str | None = None
