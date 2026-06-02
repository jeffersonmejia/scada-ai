from pydantic import BaseModel, Field

from app.schemas.classification import ClassificationResult


class ChatRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=12000)


class ChatResponse(BaseModel):
    request_id: str
    decision: str
    classification: ClassificationResult
    triggered_rules: list[str]
    response: str

