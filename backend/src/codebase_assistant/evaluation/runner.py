"""Run retrieval/answer evaluation against the fixture repository with fakes."""

from __future__ import annotations

import io
import time
import zipfile
from dataclasses import dataclass
from pathlib import Path

from codebase_assistant.adapters.extractive import ExtractiveCompleter
from codebase_assistant.adapters.lexical import LexicalEmbedder
from codebase_assistant.adapters.memory import InMemoryWorkspace
from codebase_assistant.application.ask import ask_question
from codebase_assistant.application.contracts import (
    AskQuestionRequest,
    IngestArchiveRequest,
)
from codebase_assistant.application.ingest import ingest_archive
from codebase_assistant.chunking import ChunkingLimits
from codebase_assistant.evaluation.dataset import (
    EvaluationCase,
    EvaluationDataset,
    default_dataset_path,
    load_evaluation_dataset,
)
from codebase_assistant.ingestion.limits import ArchiveLimits

_REPO_ROOT = Path(__file__).resolve().parents[4]


@dataclass(frozen=True, slots=True)
class CaseMetrics:
    case_id: str
    expect_kind: str
    latency_ms: float
    insufficient_evidence: bool
    retrieved_files: tuple[str, ...]
    cited_files: tuple[str, ...]
    source_hit_at_k: bool | None
    citation_valid: bool
    outcome_ok: bool
    answer_file_hit: bool = False
    tags: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class EvaluationReport:
    embedding_provider: str
    completion_provider: str
    retrieval_k: int
    dataset_path: str
    fixture_repository: str
    cases: tuple[CaseMetrics, ...]

    @property
    def outcome_pass_rate(self) -> float:
        if not self.cases:
            return 0.0
        return sum(1 for case in self.cases if case.outcome_ok) / len(self.cases)

    @property
    def grounded_source_hit_rate(self) -> float:
        grounded = [case for case in self.cases if case.source_hit_at_k is not None]
        if not grounded:
            return 0.0
        return sum(1 for case in grounded if case.source_hit_at_k) / len(grounded)

    @property
    def citation_validity_rate(self) -> float:
        if not self.cases:
            return 0.0
        return sum(1 for case in self.cases if case.citation_valid) / len(self.cases)

    @property
    def insufficient_evidence_correct_rate(self) -> float:
        expected = [
            case for case in self.cases if case.expect_kind == "insufficient_evidence"
        ]
        if not expected:
            return 0.0
        return sum(1 for case in expected if case.outcome_ok) / len(expected)

    @property
    def grounded_answer_file_hit_rate(self) -> float:
        grounded = [
            case
            for case in self.cases
            if case.expect_kind == "grounded" and "code_unit_details" not in case.tags
        ]
        if not grounded:
            return 0.0
        return sum(1 for case in grounded if case.answer_file_hit) / len(grounded)


def zip_fixture_repository(fixture_root: Path) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, mode="w") as archive:
        for path in sorted(fixture_root.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(fixture_root).as_posix())
    return buffer.getvalue()


def run_evaluation(
    *,
    dataset: EvaluationDataset | None = None,
    dataset_path: Path | None = None,
    repo_root: Path | None = None,
    retrieval_k: int = 5,
) -> EvaluationReport:
    root = repo_root or _REPO_ROOT
    path = dataset_path or default_dataset_path()
    loaded = dataset or load_evaluation_dataset(path)
    fixture_root = root / loaded.fixture_repository
    if not fixture_root.is_dir():
        raise FileNotFoundError(f"fixture repository missing: {fixture_root}")

    embed = LexicalEmbedder()
    complete = ExtractiveCompleter()
    store = InMemoryWorkspace()
    result = ingest_archive(
        IngestArchiveRequest(
            filename="fixture-repository.zip",
            content=zip_fixture_repository(fixture_root),
        ),
        archive_limits=ArchiveLimits(max_upload_bytes=5_000_000),
        chunk_limits=ChunkingLimits(max_lines=40, overlap_lines=0),
        embed=embed,
        store=store,
    )
    repository_id = result.repository.repository_id
    results = [
        _evaluate_case(
            case,
            repository_id=repository_id,
            embed=embed,
            store=store,
            complete=complete,
            retrieval_k=retrieval_k,
        )
        for case in loaded.cases
    ]
    return EvaluationReport(
        embedding_provider="lexical",
        completion_provider="extractive",
        retrieval_k=retrieval_k,
        dataset_path=(
            str(path.relative_to(root)) if path.is_relative_to(root) else str(path)
        ),
        fixture_repository=loaded.fixture_repository,
        cases=tuple(results),
    )


def _evaluate_case(
    case: EvaluationCase,
    *,
    repository_id: str,
    embed: LexicalEmbedder,
    store: InMemoryWorkspace,
    complete: ExtractiveCompleter,
    retrieval_k: int,
) -> CaseMetrics:
    started = time.perf_counter()
    query_vectors = embed.embed([case.question])
    hits = (
        list(store.search(repository_id, query_vectors[0], retrieval_k))
        if query_vectors
        else []
    )
    retrieved_files = tuple(dict.fromkeys(chunk.file_path for chunk in hits))
    answer = ask_question(
        AskQuestionRequest(repository_id=repository_id, question=case.question),
        embed=embed,
        search=store,
        complete=complete,
        retrieval_limit=retrieval_k,
    )
    latency_ms = (time.perf_counter() - started) * 1000.0
    cited_files = tuple(
        dict.fromkeys(citation.file_path for citation in answer.answer.citations)
    )
    excerpt_keys = {
        (item.file_path, item.start_line, item.end_line) for item in answer.excerpts
    }
    citation_valid = all(
        (citation.file_path, citation.start_line, citation.end_line) in excerpt_keys
        for citation in answer.answer.citations
    )
    if not answer.answer.citations:
        citation_valid = True
    used_files = tuple(dict.fromkeys((*retrieved_files, *cited_files)))
    blob = " ".join(
        [answer.answer.text, *[item.excerpt for item in answer.excerpts]]
    ).lower()
    source_hit: bool | None = None
    answer_file_hit = False
    if case.kind == "grounded":
        source_hit = any(path in used_files for path in case.expected_files)
        answer_file_hit = any(path in cited_files for path in case.expected_files)
        symbol_hit = all(symbol.lower() in blob for symbol in case.expected_symbols)
        if "code_unit_details" in case.tags:
            # Extractive cannot synthesize the required method table; Ollama can.
            outcome_ok = answer.answer.insufficient_evidence
        else:
            outcome_ok = answer_file_hit and symbol_hit
    else:
        outcome_ok = answer.answer.insufficient_evidence
    return CaseMetrics(
        case_id=case.case_id,
        expect_kind=case.kind,
        latency_ms=latency_ms,
        insufficient_evidence=answer.answer.insufficient_evidence,
        retrieved_files=retrieved_files,
        cited_files=cited_files,
        source_hit_at_k=source_hit,
        citation_valid=citation_valid,
        outcome_ok=outcome_ok,
        answer_file_hit=answer_file_hit,
        tags=case.tags,
    )
