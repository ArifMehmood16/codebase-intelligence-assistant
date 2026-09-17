from codebase_assistant.ops.ollama_models import (
    ensure_model,
    model_is_present,
    required_ollama_models,
)


def test_model_is_present_matches_tag_suffix() -> None:
    tags = {
        "models": [
            {"name": "nomic-embed-text:latest"},
            {"name": "llama3.2:latest"},
        ]
    }
    assert model_is_present(tags, "nomic-embed-text") is True
    assert model_is_present(tags, "nomic-embed-text:latest") is True
    assert model_is_present(tags, "mistral") is False


def test_required_models_follow_selected_providers() -> None:
    assert (
        required_ollama_models(
            embedding_provider="lexical",
            completion_provider="extractive",
            embed_model="nomic-embed-text",
            chat_model="llama3.2",
        )
        == ()
    )
    assert required_ollama_models(
        embedding_provider="ollama",
        completion_provider="extractive",
        embed_model="nomic-embed-text",
        chat_model="llama3.2",
    ) == ("nomic-embed-text",)
    assert required_ollama_models(
        embedding_provider="lexical",
        completion_provider="ollama",
        embed_model="nomic-embed-text",
        chat_model="llama3.2",
    ) == ("llama3.2",)
    assert required_ollama_models(
        embedding_provider="ollama",
        completion_provider="ollama",
        embed_model="nomic-embed-text",
        chat_model="llama3.2",
    ) == ("nomic-embed-text", "llama3.2")


def test_required_models_dedupe_when_same_tag() -> None:
    assert required_ollama_models(
        embedding_provider="ollama",
        completion_provider="ollama",
        embed_model="shared",
        chat_model="shared",
    ) == ("shared",)


def test_ensure_model_skips_pull_when_present() -> None:
    pulls: list[str] = []

    def tags() -> dict[str, object]:
        return {"models": [{"name": "nomic-embed-text:latest"}]}

    def pull(name: str) -> None:
        pulls.append(name)

    ensure_model("nomic-embed-text", list_tags=tags, pull_model=pull)
    assert pulls == []


def test_ensure_model_pulls_when_missing() -> None:
    pulls: list[str] = []

    def tags() -> dict[str, object]:
        return {"models": []}

    def pull(name: str) -> None:
        pulls.append(name)

    ensure_model("nomic-embed-text", list_tags=tags, pull_model=pull)
    assert pulls == ["nomic-embed-text"]
