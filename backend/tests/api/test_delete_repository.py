"""API coverage for deleting repositories."""

from __future__ import annotations

import io
import zipfile

from fastapi.testclient import TestClient

from codebase_assistant.adapters.memory import InMemoryWorkspace
from codebase_assistant.main import create_app


def _zip_bytes(members: dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, mode="w") as archive:
        for name, data in members.items():
            archive.writestr(name, data)
    return buffer.getvalue()


def test_delete_repository_removes_summary() -> None:
    workspace = InMemoryWorkspace()
    client = TestClient(create_app(workspace=workspace))
    created = client.post(
        "/api/repositories",
        params={"filename": "demo.zip"},
        content=_zip_bytes({"src/a.py": b"def a():\n    return 1\n"}),
        headers={"content-type": "application/zip"},
    )
    assert created.status_code == 201
    repository_id = created.json()["repository_id"]

    deleted = client.delete(f"/api/repositories/{repository_id}")
    assert deleted.status_code == 204

    listed = client.get("/api/repositories")
    assert listed.json() == {"repositories": []}
    missing = client.get(f"/api/repositories/{repository_id}")
    assert missing.status_code == 404


def test_delete_unknown_repository_returns_404() -> None:
    client = TestClient(create_app(workspace=InMemoryWorkspace()))
    response = client.delete("/api/repositories/missing-id")
    assert response.status_code == 404


def test_upload_same_name_replaces_previous_via_api() -> None:
    workspace = InMemoryWorkspace()
    client = TestClient(create_app(workspace=workspace))
    first = client.post(
        "/api/repositories",
        params={"filename": "demo.zip"},
        content=_zip_bytes({"src/old.py": b"def old():\n    return 1\n"}),
        headers={"content-type": "application/zip"},
    )
    second = client.post(
        "/api/repositories",
        params={"filename": "demo.zip"},
        content=_zip_bytes({"src/new.py": b"def new():\n    return 2\n"}),
        headers={"content-type": "application/zip"},
    )
    assert first.status_code == 201
    assert second.status_code == 201
    listed = client.get("/api/repositories").json()["repositories"]
    assert len(listed) == 1
    assert listed[0]["repository_id"] == second.json()["repository_id"]
    assert listed[0]["indexed_paths"] == ["src/new.py"]
