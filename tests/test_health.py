from fastapi.testclient import TestClient

from app.api.deps import get_mistral_client, get_roberta_client
from app.core.app_factory import create_app


class UnavailableClient:
    async def health(self) -> bool:
        return False


def test_health_degraded_when_external_services_unavailable() -> None:
    app = create_app()
    app.dependency_overrides[get_roberta_client] = lambda: UnavailableClient()
    app.dependency_overrides[get_mistral_client] = lambda: UnavailableClient()
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "degraded"
    assert response.json()["roberta_loaded"] is False
    assert response.json()["mistral_available"] is False
