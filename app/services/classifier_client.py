import logging

import httpx

from app.core.exceptions import ServiceUnavailableError
from app.schemas.classification import ClassificationResult

logger = logging.getLogger(__name__)


class ClassifierClient:
    def __init__(self, base_url: str, endpoint: str, timeout_seconds: float) -> None:
        self.base_url = base_url.rstrip("/")
        self.endpoint = endpoint if endpoint.startswith("/") else f"/{endpoint}"
        self.timeout = httpx.Timeout(timeout_seconds)

    async def health(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/health")
            return response.status_code == 200
        except httpx.HTTPError as exc:
            logger.error("Classifier health check failed: %s", exc)
            return False

    async def classify(self, text: str, request_id: str) -> ClassificationResult:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}{self.endpoint}",
                    json={"prompt": text},
                )
            if response.status_code == 503:
                raise ServiceUnavailableError("Classifier model not loaded", service="classifier")
            response.raise_for_status()
            return ClassificationResult.model_validate(response.json())
        except ServiceUnavailableError:
            raise
        except (httpx.HTTPError, ValueError) as exc:
            logger.error("Classifier request failed for %s: %s", request_id, exc)
            raise ServiceUnavailableError("Classifier API unavailable", service="classifier") from exc
