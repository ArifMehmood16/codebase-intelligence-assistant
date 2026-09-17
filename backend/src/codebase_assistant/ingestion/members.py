"""Reject ZIP members that escape the tree, exhaust limits, or inflate past a bound."""

from __future__ import annotations

import io
import zipfile
from pathlib import PurePosixPath

from codebase_assistant.ingestion.errors import RejectedArchiveError
from codebase_assistant.ingestion.limits import ArchiveLimits

_UNIX_SYMLINK_MASK = 0o170000
_UNIX_SYMLINK = 0o120000


def validate_members(content: bytes, limits: ArchiveLimits) -> None:
    try:
        archive = zipfile.ZipFile(io.BytesIO(content))
    except zipfile.BadZipFile as exc:
        raise RejectedArchiveError("archive is malformed") from exc

    with archive:
        infos = archive.infolist()
        if len(infos) > limits.max_file_count:
            raise RejectedArchiveError("archive has too many members")
        extracted = 0
        for info in infos:
            if _is_symlink(info):
                raise RejectedArchiveError("archive contains a symlink")
            _assert_safe_name(info.filename)
            if info.is_dir():
                continue
            size = info.file_size
            if size > limits.max_file_bytes:
                raise RejectedArchiveError("archive member exceeds per-file size")
            extracted += size
            if extracted > limits.max_extracted_bytes:
                raise RejectedArchiveError("extracted size exceeds limit")
            compressed = info.compress_size
            if compressed > 0 and size / compressed > limits.max_compression_ratio:
                raise RejectedArchiveError("compression ratio exceeds limit")


def read_member_bounded(
    archive: zipfile.ZipFile,
    info: zipfile.ZipInfo,
    max_bytes: int,
) -> bytes:
    """Decompress one member, stopping at max_bytes rather than trusting headers."""
    try:
        with archive.open(info) as handle:
            data = handle.read(max_bytes + 1)
    except zipfile.BadZipFile as exc:
        raise RejectedArchiveError("archive is malformed") from exc
    if len(data) > max_bytes:
        raise RejectedArchiveError("archive member exceeds per-file size")
    return data


def _is_symlink(info: zipfile.ZipInfo) -> bool:
    if info.create_system != 3:
        return False
    mode = (info.external_attr >> 16) & 0xFFFF
    return (mode & _UNIX_SYMLINK_MASK) == _UNIX_SYMLINK


def _assert_safe_name(name: str) -> None:
    if "\x00" in name:
        raise RejectedArchiveError("archive member path is invalid")
    normalised = name.replace("\\", "/")
    if normalised.startswith("/") or normalised.startswith("//"):
        raise RejectedArchiveError("archive member path is absolute")
    if len(normalised) >= 2 and normalised[1] == ":":
        raise RejectedArchiveError("archive member path is absolute")
    path = PurePosixPath(normalised)
    if path.is_absolute():
        raise RejectedArchiveError("archive member path is absolute")
    if ".." in path.parts:
        raise RejectedArchiveError("archive member path escapes the extraction root")
