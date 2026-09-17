"""Strict completion schema validation at the ask use-case boundary."""

from collections.abc import Sequence

from codebase_assistant.adapters.lexical import LexicalEmbedder
from codebase_assistant.application.ask import ask_question
from codebase_assistant.application.completion import parse_completion
from codebase_assistant.application.contracts import AskQuestionRequest
from codebase_assistant.domain import SourceChunk


def _chunk(
    file_path: str = "src/app.py",
    *,
    start: int = 1,
    end: int = 2,
    text: str = "def greet():\n    return 'hello'\n",
) -> SourceChunk:
    return SourceChunk(
        chunk_id="c1",
        repository_id="repo-1",
        file_path=file_path,
        start_line=start,
        end_line=end,
        text=text,
    )


class _FixedSearch:
    def __init__(self, chunks: Sequence[SourceChunk]) -> None:
        self._chunks = tuple(chunks)

    def search(
        self,
        repository_id: str,
        embedding: Sequence[float],
        limit: int,
    ) -> Sequence[SourceChunk]:
        return self._chunks[:limit]


def test_parse_completion_rejects_non_json() -> None:
    assert parse_completion("not-json") is None


def test_parse_completion_rejects_missing_required_keys() -> None:
    assert parse_completion('{"text":"ok","citations":[]}') is None


def test_parse_completion_rejects_wrong_field_types() -> None:
    assert (
        parse_completion('{"text":1,"citations":[],"insufficient_evidence":false}')
        is None
    )
    assert (
        parse_completion('{"text":"ok","citations":{},"insufficient_evidence":false}')
        is None
    )
    assert (
        parse_completion('{"text":"ok","citations":[],"insufficient_evidence":"false"}')
        is None
    )


def test_parse_completion_rejects_malformed_citation_entries() -> None:
    assert (
        parse_completion(
            '{"text":"ok","citations":[{"file_path":"a.py"}],'
            '"insufficient_evidence":false}'
        )
        is None
    )
    assert (
        parse_completion(
            '{"text":"ok","citations":["src/app.py"],"insufficient_evidence":false}'
        )
        is None
    )


def test_parse_completion_rejects_insufficient_flag_with_citations() -> None:
    assert (
        parse_completion(
            '{"text":"ok","citations":[{"file_path":"a.py","start_line":1,'
            '"end_line":1}],"insufficient_evidence":true}'
        )
        is None
    )


def test_parse_completion_accepts_valid_schema() -> None:
    parsed = parse_completion(
        '{"text":"greet is here","citations":[{"file_path":"src/app.py",'
        '"start_line":1,"end_line":2}],"insufficient_evidence":false}'
    )
    assert parsed is not None
    assert parsed.text == "greet is here"
    assert parsed.insufficient_evidence is False
    assert parsed.citations[0].file_path == "src/app.py"


def test_ask_malformed_completion_fails_safely_without_citations() -> None:
    class BadCompleter:
        def complete(self, prompt: str) -> str:
            return (
                '{"text":"partial","citations":[{"file_path":"src/app.py"}],'
                '"insufficient_evidence":false}'
            )

    result = ask_question(
        AskQuestionRequest(repository_id="repo-1", question="Where is greet?"),
        embed=LexicalEmbedder(),
        search=_FixedSearch([_chunk()]),
        complete=BadCompleter(),
    )
    assert result.answer.insufficient_evidence is True
    assert result.answer.citations == ()


def test_ask_drops_fabricated_citations_and_keeps_verified() -> None:
    chunk = _chunk()

    class MixedCompleter:
        def complete(self, prompt: str) -> str:
            return (
                '{"text":"greet lives in app","citations":['
                '{"file_path":"src/app.py","start_line":1,"end_line":2},'
                '{"file_path":"secret.py","start_line":1,"end_line":1},'
                '{"file_path":"src/app.py","start_line":1,"end_line":99}'
                '],"insufficient_evidence":false}'
            )

    result = ask_question(
        AskQuestionRequest(repository_id="repo-1", question="Where is greet?"),
        embed=LexicalEmbedder(),
        search=_FixedSearch([chunk]),
        complete=MixedCompleter(),
    )
    assert result.answer.insufficient_evidence is False
    assert result.answer.citations == (chunk.as_citation(),)


def test_ask_skips_completer_when_retrieval_is_empty() -> None:
    class BoomCompleter:
        def complete(self, prompt: str) -> str:
            raise AssertionError("completer must not run without evidence")

    result = ask_question(
        AskQuestionRequest(repository_id="repo-1", question="Where is greet?"),
        embed=LexicalEmbedder(),
        search=_FixedSearch(()),
        complete=BoomCompleter(),
    )
    assert result.answer.insufficient_evidence is True
    assert result.answer.citations == ()
