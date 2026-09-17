"""Deterministic lexical embeddings for tests and the short demo."""

from __future__ import annotations

import hashlib
import math
import re
from collections.abc import Sequence

from codebase_assistant.adapters.persistence import EMBEDDING_DIMENSIONS

_TOKEN = re.compile(r"[a-z0-9_]+")
_DIM = EMBEDDING_DIMENSIONS


class LexicalEmbedder:
    def embed(self, texts: Sequence[str]) -> Sequence[Sequence[float]]:
        return tuple(_vector(text) for text in texts)


def _vector(text: str) -> tuple[float, ...]:
    values = [0.0] * _DIM
    for token in _TOKEN.findall(text.lower()):
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        index = int.from_bytes(digest[:2], "big") % _DIM
        values[index] += 1.0
    norm = math.sqrt(sum(value * value for value in values))
    if norm == 0:
        return tuple(values)
    return tuple(value / norm for value in values)
