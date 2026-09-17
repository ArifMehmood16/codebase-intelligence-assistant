# ADR 004 — Local Ollama for private repository analysis

**Status:** Accepted  
**Date:** 2026-09-04  
**Deciders:** Developer

## Context

The product indexes a source-code repository and sends retrieved chunks, plus the user question, to an embedding model and an LLM. In a private deployment those repositories may be confidential: source, comments, configuration and incidental secrets must not be handed to a hosted model API as a side effect of “asking a question about the code”.

The backend already treats model access as a port. This decision chooses the first real adapter, not the application shape.

Default automated tests remain fake and must not require Ollama or any network model call.

## Decision

Use **Ollama** as the local embedding and completion runtime.

- Application code depends on narrow ports (embed, complete). The first production adapter talks to Ollama’s local HTTP API.
- Chat and embedding **model names stay configuration**. Concrete tags are chosen when Phase 5 and Phase 6 implement the adapter and are recorded then.
- Hosted LLM APIs (OpenAI, Anthropic, and similar) are not the default path for repository text.
- A private deployment runs Ollama (or an equivalent in-network OpenAI-compatible endpoint) on the organisation’s machines. Uploaded source, chunks and prompts stay inside that boundary during inference.
- Opt-in smoke tests may call local Ollama. CI and the default suite do not.

## Alternatives considered

| Alternative | Why not now |
|---|---|
| Hosted OpenAI/Anthropic (or similar) as the default | Repository contents would leave the organisation. Rejected for privacy when analysing confidential source code. |
| Hugging Face Inference API (or other hosted HF endpoints) | Same data-leaving-the-network problem as OpenAI. Hugging Face hosts many *weights*; using their cloud inference is still a hosted LLM API. |
| In-process Hugging Face Transformers / sentence-transformers | Valid local alternative: weights stay on the machine. Heavier for the current project scope (CUDA/Metal, large wheels inside the API image). Ollama already exposes local HTTP for chat and embeddings. |
| llama.cpp or vLLM invoked directly | More operational surface for the current project scope; Ollama already exposes a local HTTP API for both chat and embeddings. |
| LangChain/LlamaIndex cloud defaults | Hides the provider call and makes it easier to send source off-box accidentally. |

## Consequences

- Reviewers and internal users need a local (or in-network) Ollama process for real answers; the liveness endpoint does not.
- Quality of answers depends on the locally pulled model, not on a vendor SaaS SLA.
- Model weights may still be downloaded from Ollama’s library when first pulled. That is a supply-chain step, not an inference-time upload of repository text. Air-gapped use requires pre-loaded weights.
- Swapping to a hosted API later is an adapter change and needs a new ADR plus an explicit data-handling approval.

## Follow-up

The first embedding adapter is `OllamaEmbedder` (`POST /api/embed`). Default model tag is `nomic-embed-text` (768 dimensions, matching ADR 002). Timeout and batch size are `OLLAMA_TIMEOUT_SECONDS` and `OLLAMA_EMBED_BATCH_SIZE`. The composition root keeps `EMBEDDING_PROVIDER=lexical` so default tests and the reviewer demo do not call Ollama. Set `EMBEDDING_PROVIDER=ollama` to use the real adapter.

The first completion adapter is `OllamaCompleter` (`POST /api/chat`, non-streaming, `format: json`). Default chat model tag is `llama3.2` (`OLLAMA_CHAT_MODEL`). Temperature, output token cap and bounded retries are `LLM_TEMPERATURE`, `LLM_MAX_OUTPUT_TOKENS` and `LLM_MAX_RETRIES`. The composition root keeps `COMPLETION_PROVIDER=extractive` so default tests and offline demos do not call Ollama. Set `COMPLETION_PROVIDER=ollama` to use the real adapter. `make run` and `make run-docker` pull whichever of `OLLAMA_EMBED_MODEL` / `OLLAMA_CHAT_MODEL` the selected providers require. Do not send source, chunks or prompts to a hosted LLM from application code.
