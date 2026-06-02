import logging

import httpx

from app.core.exceptions import ServiceUnavailableError

logger = logging.getLogger(__name__)


class OllamaClient:
    def __init__(self, base_url: str, model: str, timeout_seconds: float) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = httpx.Timeout(timeout_seconds)

    async def health(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except httpx.HTTPError as exc:
            logger.error("Ollama health check failed: %s", exc)
            return False

    async def generate(self, prompt: str, request_id: str) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.2},
        }
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(f"{self.base_url}/api/generate", json=payload)
            if response.status_code >= 500:
                raise ServiceUnavailableError("Ollama service unavailable", service="ollama")
            response.raise_for_status()
            data = response.json()
            return str(data.get("response", ""))
        except (httpx.HTTPError, ValueError) as exc:
            logger.error("Ollama request failed for %s: %s", request_id, exc)
            raise ServiceUnavailableError("Ollama service unavailable", service="ollama") from exc

