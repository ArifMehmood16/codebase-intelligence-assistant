"""Ingestion summary counts members without returning secret contents."""

from __future__ import annotations

import io
import zipfile
from pathlib import Path

import pytest

from codebase_assistant.ingestion.errors import RejectedArchiveError
from codebase_assistant.ingestion.limits import ArchiveLimits
from codebase_assistant.ingestion.summary import summarise_archive

_LIMITS = ArchiveLimits(max_upload_bytes=1024 * 1024)


def _zip_bytes(members: dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, mode="w") as archive:
        for name, data in members.items():
            archive.writestr(name, data)
    return buffer.getvalue()


def test_valid_archive_returns_sorted_counts_without_secret_contents() -> None:
    content = _zip_bytes(
        {
            "src/app.py": b"print(1)\n",
            "README.md": b"hello\n",
            "config/.env.production": b"SECRET=super-secret\n",
            "frontend/node_modules/leftpad/index.js": b"module.exports=1\n",
        }
    )

    summary = summarise_archive(content, "repo.zip", _LIMITS)

    assert summary.indexed_file_count == 2
    assert summary.ignored_file_count == 2
    assert [member.relative_path for member in summary.accepted] == [
        "README.md",
        "src/app.py",
    ]
    assert [member.relative_path for member in summary.ignored] == [
        "config/.env.production",
        "frontend/node_modules/leftpad/index.js",
    ]
    assert summary.ignored_reason_counts == (
        ("excluded_directory", 1),
        ("secret_file", 1),
    )
    assert "super-secret" not in repr(summary)
    for member in summary.ignored:
        assert not hasattr(member, "text")


def test_directory_entries_are_not_counted() -> None:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, mode="w") as archive:
        archive.writestr("src/", b"")
        archive.writestr("src/app.py", b"print(1)\n")

    summary = summarise_archive(buffer.getvalue(), "repo.zip", _LIMITS)

    assert summary.indexed_file_count == 1
    assert summary.ignored_file_count == 0
    assert summary.accepted[0].relative_path == "src/app.py"


def test_repository_python_is_not_executed() -> None:
    summary = summarise_archive(
        _zip_bytes({"boom.py": b"raise SystemExit('executed')\n"}),
        "repo.zip",
        _LIMITS,
    )
    assert summary.accepted[0].text == "raise SystemExit('executed')\n"


def test_invalid_utf8_is_ignored_without_raising() -> None:
    summary = summarise_archive(
        _zip_bytes({"readme.md": b"\xff\xfe not utf-8"}),
        "repo.zip",
        _LIMITS,
    )
    assert summary.ignored[0].reason == "encoding"
    assert summary.indexed_file_count == 0


def test_high_ratio_member_is_rejected_without_decompressing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    zeros = b"\x00" * 5_000
    info = zipfile.ZipInfo("zeros.bin")
    info.compress_type = zipfile.ZIP_DEFLATED
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, mode="w") as archive:
        archive.writestr(info, zeros)
    limits = ArchiveLimits(
        max_upload_bytes=1024 * 1024,
        max_file_count=10,
        max_file_bytes=50_000,
        max_extracted_bytes=50_000,
        max_compression_ratio=2.0,
    )

    def fail_if_decompressed(*_args: object, **_kwargs: object) -> None:
        raise AssertionError("members must not be decompressed before size limits")

    monkeypatch.setattr(zipfile.ZipFile, "testzip", fail_if_decompressed)
    monkeypatch.setattr(zipfile.ZipFile, "read", fail_if_decompressed)
    with pytest.raises(RejectedArchiveError, match="compression ratio"):
        summarise_archive(buffer.getvalue(), "repo.zip", limits)


def test_temporary_dir_is_removed_after_success(tmp_path: Path) -> None:
    summarise_archive(
        _zip_bytes({"app.py": b"print(1)\n"}),
        "repo.zip",
        _LIMITS,
        work_dir=tmp_path,
    )
    assert list(tmp_path.iterdir()) == []


def test_temporary_dir_is_removed_when_archive_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(RejectedArchiveError):
        summarise_archive(b"not a zip", "repo.zip", _LIMITS, work_dir=tmp_path)
    assert list(tmp_path.iterdir()) == []


def test_temporary_dir_is_removed_when_processing_raises(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def boom(_relative_path: str, _data: bytes) -> None:
        raise RuntimeError("classify failed")

    monkeypatch.setattr(
        "codebase_assistant.ingestion.summary.classify_source_file",
        boom,
    )
    with pytest.raises(RuntimeError, match="classify failed"):
        summarise_archive(
            _zip_bytes({"app.py": b"print(1)\n"}),
            "repo.zip",
            _LIMITS,
            work_dir=tmp_path,
        )
    assert list(tmp_path.iterdir()) == []
