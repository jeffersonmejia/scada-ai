import logging

import httpx

from app.core.exceptions import ServiceUnavailableError

logger = logging.getLogger(__name__)


class MistralClient:
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
            logger.error("Mistral health check failed: %s", exc)
            return False

    async def generate(self, prompt: str, request_id: str) -> str:
        payload = {
            "prompt": prompt,
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}{self.endpoint}",
                    json=payload,
                )
            if response.status_code >= 500:
                raise ServiceUnavailableError("Mistral API unavailable", service="mistral")
            response.raise_for_status()
            data = response.json()
            return str(data.get("response") or data.get("message") or data.get("text") or "")
        except (httpx.HTTPError, ValueError) as exc:
            logger.error("Mistral request failed for %s: %s", request_id, exc)
            raise ServiceUnavailableError("Mistral API unavailable", service="mistral") from exc
