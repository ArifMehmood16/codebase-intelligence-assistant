"""Admit a ZIP upload before any archive member is decompressed."""

from __future__ import annotations

import io
import zipfile

from codebase_assistant.ingestion.errors import RejectedArchiveError
from codebase_assistant.ingestion.limits import ArchiveLimits

_ZIP_SUFFIX = ".zip"


def admit_archive(content: bytes, filename: str, limits: ArchiveLimits) -> None:
    if not filename.lower().endswith(_ZIP_SUFFIX):
        raise RejectedArchiveError("archive filename must end with .zip")
    if len(content) > limits.max_upload_bytes:
        raise RejectedArchiveError("archive exceeds configured upload size")
    try:
        with zipfile.ZipFile(io.BytesIO(content)):
            pass
    except zipfile.BadZipFile as exc:
        raise RejectedArchiveError("archive is malformed") from exc
