"""HTTP application factory for the Codebase Intelligence Assistant API."""

import sys
from typing import Literal

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict, ValidationError

from codebase_assistant.adapters.extractive import ExtractiveCompleter
from codebase_assistant.adapters.lexical import LexicalEmbedder
from codebase_assistant.adapters.memory import InMemoryWorkspace
from codebase_assistant.adapters.ollama import OllamaCompleter, OllamaEmbedder
from codebase_assistant.adapters.postgres import PostgresWorkspace, create_db_engine
from codebase_assistant.application.ask import ask_question
from codebase_assistant.application.contracts import (
    AskQuestionRequest,
    IngestArchiveRequest,
    IngestArchiveResult,
)
from codebase_assistant.application.errors import CompletionError
from codebase_assistant.application.ingest import ingest_archive
from codebase_assistant.application.limits import AnswerLimits
from codebase_assistant.application.ports import (
    CompleteAnswer,
    EmbedTexts,
    IngestionStore,
)
from codebase_assistant.application.repository_card import card_to_payload
from codebase_assistant.chunking import ChunkingLimits
from codebase_assistant.config import Settings, load_settings
from codebase_assistant.domain import InvalidQuestionError
from codebase_assistant.ingestion.errors import RejectedArchiveError
from codebase_assistant.ingestion.limits import ArchiveLimits

_ALLOWED_UPLOAD_TYPES = frozenset(
    {
        "application/zip",
        "application/octet-stream",
        "application/x-zip-compressed",
    }
)


class LivenessResponse(BaseModel):
    """Process liveness: no dependency checks."""

    model_config = ConfigDict(frozen=True)

    status: Literal["ok"]


class QuestionRequest(BaseModel):
    model_config = ConfigDict(frozen=True)

    question: str


def create_app(
    workspace: IngestionStore | None = None,
    embed: EmbedTexts | None = None,
    complete: CompleteAnswer | None = None,
) -> FastAPI:
    settings = _try_settings()
    store = workspace if workspace is not None else _default_store(settings)
    embedder = embed if embed is not None else _default_embedder(settings)
    completer = complete if complete is not None else _default_completer(settings)
    cors_origins, archive_limits, chunk_limits, answer_limits = _runtime_limits(
        settings
    )

    app = FastAPI(title="Codebase Intelligence Assistant")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/health/live", response_model=LivenessResponse)
    def live() -> LivenessResponse:
        return LivenessResponse(status="ok")

    @app.post("/api/repositories", status_code=201)
    async def upload_repository(
        request: Request,
        filename: str = Query(min_length=1),
    ) -> dict[str, object]:
        content_type = (request.headers.get("content-type") or "").split(";")[0]
        if content_type.strip().lower() not in _ALLOWED_UPLOAD_TYPES:
            raise HTTPException(
                status_code=415,
                detail="ZIP uploads must use application/zip",
            )
        content = await request.body()
        if len(content) > archive_limits.max_upload_bytes:
            raise HTTPException(
                status_code=413,
                detail="archive exceeds configured upload size",
            )
        try:
            result = ingest_archive(
                IngestArchiveRequest(filename=filename, content=content),
                archive_limits=archive_limits,
                chunk_limits=chunk_limits,
                embed=embedder,
                store=store,
            )
        except RejectedArchiveError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return _summary_payload(result)

    @app.get("/api/repositories")
    def list_repositories() -> dict[str, object]:
        return {
            "repositories": [
                _summary_payload(summary) for summary in store.list_summaries()
            ]
        }

    @app.get("/api/repositories/{repository_id}")
    def get_repository(repository_id: str) -> dict[str, object]:
        summary = store.get_summary(repository_id)
        if summary is None:
            raise HTTPException(status_code=404, detail="repository not found")
        return _summary_payload(summary)

    @app.delete("/api/repositories/{repository_id}", status_code=204)
    def delete_repository(repository_id: str) -> None:
        if not store.delete_repository(repository_id):
            raise HTTPException(status_code=404, detail="repository not found")

    @app.post("/api/repositories/{repository_id}/questions")
    def ask_repository_question(
        repository_id: str,
        body: QuestionRequest,
    ) -> dict[str, object]:
        summary = store.get_summary(repository_id)
        if summary is None:
            raise HTTPException(status_code=404, detail="repository not found")
        if summary.status != "completed":
            raise HTTPException(
                status_code=409,
                detail="repository is not indexed",
            )
        try:
            result = ask_question(
                AskQuestionRequest(
                    repository_id=repository_id,
                    question=body.question,
                ),
                embed=embedder,
                search=store,
                complete=completer,
                answer_limits=answer_limits,
            )
        except InvalidQuestionError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except CompletionError as exc:
            raise HTTPException(
                status_code=503,
                detail="completion provider unavailable",
            ) from exc
        return {
            "text": result.answer.text,
            "insufficient_evidence": result.answer.insufficient_evidence,
            "citations": [
                {
                    "file_path": excerpt.file_path,
                    "start_line": excerpt.start_line,
                    "end_line": excerpt.end_line,
                    "excerpt": excerpt.excerpt,
                }
                for excerpt in result.excerpts
            ],
        }

    return app


def _summary_payload(result: IngestArchiveResult) -> dict[str, object]:
    return {
        "repository_id": result.repository.repository_id,
        "status": result.status,
        "indexed_file_count": result.indexed_file_count,
        "ignored_file_count": result.ignored_file_count,
        "ignored_reason_counts": [
            {"reason": reason, "count": count}
            for reason, count in result.ignored_reason_counts
        ],
        "indexed_paths": list(result.indexed_paths),
        "failure_code": result.failure_code,
        "source_filename": result.source_filename,
        "repository_card": (
            card_to_payload(result.card) if result.card is not None else None
        ),
    }


def _try_settings() -> Settings | None:
    try:
        return load_settings()
    except ValidationError:
        return None


def _runtime_limits(
    settings: Settings | None,
) -> tuple[list[str], ArchiveLimits, ChunkingLimits, AnswerLimits]:
    if settings is None:
        origin = "http://localhost:3000"
        return (
            _cors_origins(origin),
            ArchiveLimits(max_upload_bytes=10_485_760),
            ChunkingLimits(),
            AnswerLimits(),
        )
    return (
        _cors_origins(settings.cors_allow_origin),
        ArchiveLimits(
            max_upload_bytes=settings.max_archive_bytes,
            max_file_count=settings.max_archive_file_count,
            max_file_bytes=settings.max_archive_file_bytes,
            max_extracted_bytes=settings.max_archive_extracted_bytes,
            max_compression_ratio=settings.max_archive_compression_ratio,
        ),
        ChunkingLimits(),
        AnswerLimits(
            max_question_chars=settings.max_question_chars,
            max_context_chars=settings.max_context_chars,
            max_excerpt_chars=settings.max_excerpt_chars,
        ),
    )


def _cors_origins(origin: str) -> list[str]:
    """Allow localhost and 127.0.0.1 as the same configured frontend origin."""
    allowed = [origin]
    if "://localhost" in origin:
        allowed.append(origin.replace("://localhost", "://127.0.0.1", 1))
    elif "://127.0.0.1" in origin:
        allowed.append(origin.replace("://127.0.0.1", "://localhost", 1))
    return allowed


def _running_under_pytest() -> bool:
    # Keep default tests hermetic even when a developer .env selects Ollama/Postgres.
    return "pytest" in sys.modules


def _default_store(settings: Settings | None) -> IngestionStore:
    if _running_under_pytest():
        return InMemoryWorkspace()
    url = settings.postgres_url() if settings is not None else None
    if url:
        return PostgresWorkspace(create_db_engine(url))
    return InMemoryWorkspace()


def _default_embedder(settings: Settings | None) -> EmbedTexts:
    if _running_under_pytest():
        return LexicalEmbedder()
    if settings is not None and settings.embedding_provider == "ollama":
        return OllamaEmbedder(
            host=settings.ollama_host,
            model=settings.ollama_embed_model,
            timeout_seconds=settings.ollama_timeout_seconds,
            batch_size=settings.ollama_embed_batch_size,
        )
    return LexicalEmbedder()


def _default_completer(settings: Settings | None) -> CompleteAnswer:
    if _running_under_pytest():
        return ExtractiveCompleter()
    if settings is not None and settings.completion_provider == "ollama":
        return OllamaCompleter(
            host=settings.ollama_host,
            model=settings.ollama_chat_model,
            temperature=settings.llm_temperature,
            max_output_tokens=settings.llm_max_output_tokens,
            timeout_seconds=settings.ollama_timeout_seconds,
            max_retries=settings.llm_max_retries,
        )
    return ExtractiveCompleter()


app = create_app()
