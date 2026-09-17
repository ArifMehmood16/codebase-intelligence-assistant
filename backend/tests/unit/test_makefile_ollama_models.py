"""Make targets must ensure Ollama models for selected providers."""

from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
_MAKEFILE = (_REPO_ROOT / "Makefile").read_text(encoding="utf-8")


def test_makefile_ensures_models_for_run_and_run_docker() -> None:
    assert "ensure-ollama-models:" in _MAKEFILE
    run_docker = _MAKEFILE.split("run-docker:")[1].split("\n# Host API")[0]
    assert "ensure-ollama-models" in run_docker
    run = _MAKEFILE.split("\nrun:")[1].split("\nensure-ollama-models:")[0]
    assert "ensure-ollama-models" in run
    assert "--embedding-provider" in _MAKEFILE
    assert "--completion-provider" in _MAKEFILE
    assert "--embed-model" in _MAKEFILE
    assert "--chat-model" in _MAKEFILE
