from fastapi.testclient import TestClient

from app.api.deps import get_audit_service, get_classifier_client, get_qwen_client
from app.core.app_factory import create_app
from app.schemas.classification import ClassificationResult


class FakeClassifierClient:
    async def classify(self, prompt: str, request_id: str) -> ClassificationResult:
        return ClassificationResult(label="safe", score=0.99)


class FakeQwenClient:
    async def generate(self, prompt: str, request_id: str) -> str:
        return "safe response"


class FakeAuditService:
    async def record(self, event) -> None:
        return None


def test_chat_accepts_internal_request_without_api_key(monkeypatch) -> None:
    app = create_app()
    app.dependency_overrides[get_classifier_client] = lambda: FakeClassifierClient()
    app.dependency_overrides[get_qwen_client] = lambda: FakeQwenClient()
    app.dependency_overrides[get_audit_service] = lambda: FakeAuditService()
    client = TestClient(app)

    response = client.post("/api/chat", json={"prompt": "hello"})

    assert response.status_code == 200
    assert response.json()["decision"] == "allowed"
