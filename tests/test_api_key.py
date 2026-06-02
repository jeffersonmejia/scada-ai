from fastapi.testclient import TestClient

from app.core.app_factory import create_app


def test_chat_requires_api_key(monkeypatch) -> None:
    monkeypatch.setenv("SERVICE_ROLE", "middleware")
    monkeypatch.setenv("API_KEY", "test-key")
    app = create_app()
    client = TestClient(app)

    response = client.post("/api/chat", json={"prompt": "hello"})

    assert response.status_code == 401
    assert response.json()["message"] == "Invalid or missing API key"

