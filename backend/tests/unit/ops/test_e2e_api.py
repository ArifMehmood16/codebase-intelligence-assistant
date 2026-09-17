"""Smoke-cover the deterministic e2e API process entrypoint."""

from __future__ import annotations

from codebase_assistant.ops import e2e_api


def test_e2e_api_main_starts_uvicorn_with_fakes(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_run(app: object, *, host: str, port: int, log_level: str) -> None:
        captured["app"] = app
        captured["host"] = host
        captured["port"] = port
        captured["log_level"] = log_level

    monkeypatch.setattr(e2e_api.uvicorn, "run", fake_run)
    assert e2e_api.main(["--host", "127.0.0.1", "--port", "8010"]) == 0
    assert captured["host"] == "127.0.0.1"
    assert captured["port"] == 8010
    assert captured["log_level"] == "warning"
    assert captured["app"] is not None
