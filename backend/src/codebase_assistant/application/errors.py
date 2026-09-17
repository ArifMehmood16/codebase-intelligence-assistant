"""Application-level failures. Safe to map at HTTP boundaries."""


class EmbeddingError(Exception):
    """The embedding provider failed. Message must not contain source text."""


class CompletionError(Exception):
    """The completion provider failed. Message must not contain prompts or source."""
