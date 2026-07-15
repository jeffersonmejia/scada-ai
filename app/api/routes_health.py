from fastapi import APIRouter, Depends

from app.api.deps import get_classifier_client, get_qwen_client
from app.schemas.health import HealthResponse
from app.services.classifier_client import ClassifierClient
from app.services.qwen_client import QwenClient

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health(
    classifier_client: ClassifierClient = Depends(get_classifier_client),
    qwen_client: QwenClient = Depends(get_qwen_client),
) -> HealthResponse:
    errors: list[str] = []

    classifier_loaded = await classifier_client.health()
    qwen_available = await qwen_client.health()
    if not classifier_loaded:
        errors.append("Classifier API unavailable")
    if not qwen_available:
        errors.append("Qwen API unavailable")

    return HealthResponse(
        status="healthy" if not errors else "degraded",
        classifier_loaded=classifier_loaded,
        qwen_available=qwen_available,
        error="; ".join(errors) if errors else None,
    )
