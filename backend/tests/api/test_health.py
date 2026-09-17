from fastapi.testclient import TestClient

from codebase_assistant.main import create_app


def test_liveness_returns_ok_status() -> None:
    client = TestClient(create_app())

    response = client.get("/api/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
