import io
import zipfile

from fastapi.testclient import TestClient

from codebase_assistant.adapters.memory import InMemoryWorkspace
from codebase_assistant.application.errors import EmbeddingError
from codebase_assistant.main import create_app


def _zip_bytes(members: dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, mode="w") as archive:
        for name, data in members.items():
            archive.writestr(name, data)
    return buffer.getvalue()


def test_upload_zip_returns_ingestion_summary() -> None:
    client = TestClient(create_app(workspace=InMemoryWorkspace()))
    response = client.post(
        "/api/repositories",
        params={"filename": "repo.zip"},
        content=_zip_bytes(
            {
                "src/app.py": b"def greet():\n    return 'hello'\n",
                "config/.env": b"SECRET=nope\n",
            }
        ),
        headers={"content-type": "application/zip"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["indexed_file_count"] == 1
    assert body["ignored_file_count"] == 1
    assert body["indexed_paths"] == ["src/app.py"]
    assert "repository_id" in body
    assert "SECRET" not in response.text


def test_upload_and_get_return_repository_card() -> None:
    client = TestClient(create_app(workspace=InMemoryWorkspace()))
    response = client.post(
        "/api/repositories",
        params={"filename": "inventory.zip"},
        content=_zip_bytes(
            {
                "README.md": b"# Inventory service\n",
                "src/app.py": b"def greet():\n    return 'hello'\n",
            }
        ),
        headers={"content-type": "application/zip"},
    )
    assert response.status_code == 201
    card = response.json()["repository_card"]
    assert card["display_name"] == "inventory"
    assert card["readme_path"] == "README.md"
    assert "inventory" in card["readme_excerpt"].lower()
    assert "src/app.py" in card["outline_paths"]
    fetched = client.get(f"/api/repositories/{response.json()['repository_id']}")
    assert fetched.status_code == 200
    assert fetched.json()["repository_card"] == card


def test_upload_rejects_wrong_content_type() -> None:
    client = TestClient(create_app(workspace=InMemoryWorkspace()))
    response = client.post(
        "/api/repositories",
        params={"filename": "repo.zip"},
        content=_zip_bytes({"a.py": b"x=1\n"}),
        headers={"content-type": "text/plain"},
    )
    assert response.status_code == 415


def test_question_returns_verified_citation() -> None:
    client = TestClient(create_app(workspace=InMemoryWorkspace()))
    uploaded = client.post(
        "/api/repositories",
        params={"filename": "repo.zip"},
        content=_zip_bytes({"src/app.py": b"def greet():\n    return 'hello'\n"}),
        headers={"content-type": "application/zip"},
    )
    repository_id = uploaded.json()["repository_id"]
    response = client.post(
        f"/api/repositories/{repository_id}/questions",
        json={"question": "Where is greet defined?"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["insufficient_evidence"] is False
    assert body["citations"][0]["file_path"] == "src/app.py"
    assert "greet" in body["citations"][0]["excerpt"]


def test_failed_upload_does_not_look_completed() -> None:
    class BoomEmbedder:
        def embed(self, texts: object) -> object:
            raise EmbeddingError("embedding provider timed out")

    client = TestClient(create_app(workspace=InMemoryWorkspace(), embed=BoomEmbedder()))
    response = client.post(
        "/api/repositories",
        params={"filename": "repo.zip"},
        content=_zip_bytes({"src/app.py": b"def greet():\n    return 'hello'\n"}),
        headers={"content-type": "application/zip"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "failed"
    assert body["failure_code"] == "embedding_failed"
    assert body["indexed_file_count"] == 0
    ask = client.post(
        f"/api/repositories/{body['repository_id']}/questions",
        json={"question": "Where is greet defined?"},
    )
    assert ask.status_code == 409


def test_missing_repository_returns_404() -> None:
    client = TestClient(create_app(workspace=InMemoryWorkspace()))
    response = client.post(
        "/api/repositories/missing/questions",
        json={"question": "Where is greet?"},
    )
    assert response.status_code == 404


def test_completion_failure_returns_safe_503() -> None:
    from codebase_assistant.adapters.lexical import LexicalEmbedder
    from codebase_assistant.application.errors import CompletionError

    class BoomCompleter:
        def complete(self, prompt: str) -> str:
            raise CompletionError("completion provider timed out")

    client = TestClient(
        create_app(
            workspace=InMemoryWorkspace(),
            embed=LexicalEmbedder(),
            complete=BoomCompleter(),
        )
    )
    uploaded = client.post(
        "/api/repositories",
        params={"filename": "repo.zip"},
        content=_zip_bytes({"src/app.py": b"def greet():\n    return 'hello'\n"}),
        headers={"content-type": "application/zip"},
    )
    repository_id = uploaded.json()["repository_id"]
    response = client.post(
        f"/api/repositories/{repository_id}/questions",
        json={"question": "Where is greet defined?"},
    )
    assert response.status_code == 503
    assert response.json()["detail"] == "completion provider unavailable"
    assert "timed out" not in response.text
