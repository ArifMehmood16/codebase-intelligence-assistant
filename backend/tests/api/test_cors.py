import pytest
from fastapi.testclient import TestClient

from codebase_assistant.adapters.memory import InMemoryWorkspace
from codebase_assistant.main import create_app


def test_cors_preflight_allows_loopback_alias(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CORS_ALLOW_ORIGIN", "http://localhost:3000")
    client = TestClient(create_app(workspace=InMemoryWorkspace()))
    response = client.options(
        "/api/repositories",
        params={"filename": "repo.zip"},
        headers={
            "Origin": "http://127.0.0.1:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )
    assert response.status_code in {200, 204}
    assert response.headers["access-control-allow-origin"] == "http://127.0.0.1:3000"
    assert "POST" in response.headers.get("access-control-allow-methods", "")
