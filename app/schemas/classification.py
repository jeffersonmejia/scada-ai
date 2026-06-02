from pydantic import BaseModel, Field


class ClassificationRequest(BaseModel):
    text: str = Field(min_length=1, max_length=12000)
    request_id: str | None = None


class ClassificationResult(BaseModel):
    label: str
    score: float = Field(ge=0.0, le=1.0)

