from datetime import UTC, datetime

from pydantic import BaseModel, Field


class AuditEvent(BaseModel):
    request_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    client_host: str | None = None
    prompt: str
    roberta_label: str
    roberta_score: float
    triggered_rules: list[str]
    final_decision: str
    generated_response: str
    classification_ms: float
    inference_ms: float
    validation_ms: float
    total_ms: float

