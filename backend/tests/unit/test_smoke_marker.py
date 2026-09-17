"""Default pytest must not run live Ollama smoke tests."""

from pathlib import Path

_PYPROJECT = (
    Path(__file__).resolve().parents[3] / "backend" / "pyproject.toml"
).read_text(encoding="utf-8")


def test_default_pytest_excludes_smoke_marker() -> None:
    assert "smoke: requires local Ollama and RUN_LLM_SMOKE=1" in _PYPROJECT
    assert "not integration and not smoke" in _PYPROJECT
