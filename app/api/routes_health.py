from fastapi import APIRouter, Depends

from app.api.deps import get_ollama_client, get_roberta_classifier, get_roberta_client, get_settings
from app.core.config import Settings
from app.schemas.health import HealthResponse
from app.services.ollama_client import OllamaClient
from app.services.roberta_client import RobertaClient
from app.services.roberta_service import RobertaClassifier

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health(
    settings: Settings = Depends(get_settings),
    classifier: RobertaClassifier = Depends(get_roberta_classifier),
    roberta_client: RobertaClient = Depends(get_roberta_client),
    ollama_client: OllamaClient = Depends(get_ollama_client),
) -> HealthResponse:
    errors: list[str] = []

    if settings.service_role == "classifier":
        roberta_loaded = classifier.loaded
        ollama_available = None
        if classifier.error:
            errors.append(classifier.error)
    else:
        roberta_loaded = await roberta_client.health()
        ollama_available = await ollama_client.health()
        if not roberta_loaded:
            errors.append("RoBERTa classifier service unavailable")
        if not ollama_available:
            errors.append("Ollama service unavailable")

    return HealthResponse(
        status="healthy" if not errors else "degraded",
        roberta_loaded=roberta_loaded,
        ollama_available=ollama_available,
        error="; ".join(errors) if errors else None,
    )

