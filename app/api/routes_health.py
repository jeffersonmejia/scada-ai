from fastapi import APIRouter, Depends

from app.api.deps import get_mistral_client, get_roberta_client
from app.schemas.health import HealthResponse
from app.services.mistral_client import MistralClient
from app.services.roberta_client import RobertaClient

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health(
    roberta_client: RobertaClient = Depends(get_roberta_client),
    mistral_client: MistralClient = Depends(get_mistral_client),
) -> HealthResponse:
    errors: list[str] = []

    roberta_loaded = await roberta_client.health()
    mistral_available = await mistral_client.health()
    if not roberta_loaded:
        errors.append("RoBERTa API unavailable")
    if not mistral_available:
        errors.append("Mistral API unavailable")

    return HealthResponse(
        status="healthy" if not errors else "degraded",
        roberta_loaded=roberta_loaded,
        mistral_available=mistral_available,
        error="; ".join(errors) if errors else None,
    )
