from fastapi.testclient import TestClient

from app.core.app_factory import create_app


def test_classifier_health_degraded_when_model_missing(monkeypatch, tmp_path) -> None:
    monkeypatch.setenv("SERVICE_ROLE", "classifier")
    monkeypatch.setenv("ROBERTA_MODEL_PATH", str(tmp_path / "missing_model"))
    app = create_app()
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "degraded"
    assert response.json()["roberta_loaded"] is False

