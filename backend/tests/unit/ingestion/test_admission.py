"""Untrusted ZIP bytes must be admitted before any member is read."""

import io
import zipfile

import pytest

from codebase_assistant.ingestion.admission import admit_archive
from codebase_assistant.ingestion.errors import RejectedArchiveError
from codebase_assistant.ingestion.limits import ArchiveLimits


def _zip_bytes(members: dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, mode="w") as archive:
        for name, data in members.items():
            archive.writestr(name, data)
    return buffer.getvalue()


def test_rejects_non_zip_bytes() -> None:
    with pytest.raises(RejectedArchiveError):
        admit_archive(
            content=b"this is not a zip",
            filename="repo.zip",
            limits=ArchiveLimits(max_upload_bytes=1024),
        )


def test_rejects_upload_over_configured_size() -> None:
    content = _zip_bytes({"readme.md": b"ok"})
    with pytest.raises(RejectedArchiveError):
        admit_archive(
            content=content,
            filename="repo.zip",
            limits=ArchiveLimits(max_upload_bytes=len(content) - 1),
        )


def test_rejects_filename_that_is_not_zip() -> None:
    with pytest.raises(RejectedArchiveError):
        admit_archive(
            content=_zip_bytes({"a.py": b"x = 1\n"}),
            filename="repo.tar",
            limits=ArchiveLimits(max_upload_bytes=1024),
        )


def test_rejects_malformed_zip() -> None:
    with pytest.raises(RejectedArchiveError):
        admit_archive(
            content=b"PK\x03\x04truncated",
            filename="repo.zip",
            limits=ArchiveLimits(max_upload_bytes=1024),
        )


def test_admits_small_valid_zip() -> None:
    content = _zip_bytes({"app.py": b"print(1)\n"})
    admit_archive(
        content=content,
        filename="repo.zip",
        limits=ArchiveLimits(max_upload_bytes=1024 * 1024),
    )


def test_admit_does_not_decompress_members(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_testzip(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("admission must not call testzip")

    monkeypatch.setattr(zipfile.ZipFile, "testzip", fail_testzip)
    admit_archive(
        content=_zip_bytes({"app.py": b"print(1)\n"}),
        filename="repo.zip",
        limits=ArchiveLimits(max_upload_bytes=1024 * 1024),
    )
