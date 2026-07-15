from fastapi.testclient import TestClient

from app.api.deps import get_classifier_client, get_qwen_client
from app.core.app_factory import create_app


class UnavailableClient:
    async def health(self) -> bool:
        return False


def test_health_degraded_when_external_services_unavailable() -> None:
    app = create_app()
    app.dependency_overrides[get_classifier_client] = lambda: UnavailableClient()
    app.dependency_overrides[get_qwen_client] = lambda: UnavailableClient()
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "degraded"
    assert response.json()["classifier_loaded"] is False
    assert response.json()["qwen_available"] is False
