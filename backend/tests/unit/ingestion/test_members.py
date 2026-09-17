"""Archive members must not escape the extraction root or exhaust resources."""

import io
import zipfile

import pytest

from codebase_assistant.ingestion.errors import RejectedArchiveError
from codebase_assistant.ingestion.limits import ArchiveLimits
from codebase_assistant.ingestion.members import read_member_bounded, validate_members

_LIMITS = ArchiveLimits(
    max_upload_bytes=1024 * 1024,
    max_file_count=10,
    max_file_bytes=8_000,
    max_extracted_bytes=16_000,
    max_compression_ratio=20.0,
)


def _zip_bytes(members: dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, mode="w") as archive:
        for name, data in members.items():
            archive.writestr(name, data)
    return buffer.getvalue()


def _zip_with_infos(entries: list[tuple[zipfile.ZipInfo, bytes]]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, mode="w") as archive:
        for info, data in entries:
            archive.writestr(info, data)
    return buffer.getvalue()


def test_rejects_parent_directory_traversal() -> None:
    with pytest.raises(RejectedArchiveError):
        validate_members(
            _zip_bytes({"../secret.py": b"x = 1\n"}),
            limits=_LIMITS,
        )


def test_rejects_nested_traversal() -> None:
    with pytest.raises(RejectedArchiveError):
        validate_members(
            _zip_bytes({"src/../../outside.py": b"x = 1\n"}),
            limits=_LIMITS,
        )


def test_rejects_absolute_posix_path() -> None:
    with pytest.raises(RejectedArchiveError):
        validate_members(
            _zip_bytes({"/etc/passwd": b"root\n"}),
            limits=_LIMITS,
        )


def test_rejects_windows_absolute_path() -> None:
    with pytest.raises(RejectedArchiveError):
        validate_members(
            _zip_bytes({"C:/Windows/system32/config": b"x"}),
            limits=_LIMITS,
        )


def test_rejects_symlink_member() -> None:
    info = zipfile.ZipInfo("rel_link")
    info.create_system = 3
    info.external_attr = 0xA1ED0000
    with pytest.raises(RejectedArchiveError):
        validate_members(
            _zip_with_infos([(info, b"/tmp/secret")]),
            limits=_LIMITS,
        )


def test_rejects_too_many_files() -> None:
    members = {f"f{i}.txt": b"x" for i in range(3)}
    limits = ArchiveLimits(
        max_upload_bytes=1024 * 1024,
        max_file_count=2,
        max_file_bytes=8_000,
        max_extracted_bytes=16_000,
        max_compression_ratio=20.0,
    )
    with pytest.raises(RejectedArchiveError):
        validate_members(_zip_bytes(members), limits=limits)


def test_rejects_per_file_size() -> None:
    limits = ArchiveLimits(
        max_upload_bytes=1024 * 1024,
        max_file_count=10,
        max_file_bytes=10,
        max_extracted_bytes=16_000,
        max_compression_ratio=20.0,
    )
    with pytest.raises(RejectedArchiveError):
        validate_members(_zip_bytes({"big.txt": b"0123456789abcdef"}), limits=limits)


def test_rejects_total_extracted_size() -> None:
    limits = ArchiveLimits(
        max_upload_bytes=1024 * 1024,
        max_file_count=10,
        max_file_bytes=8_000,
        max_extracted_bytes=19,
        max_compression_ratio=20.0,
    )
    with pytest.raises(RejectedArchiveError):
        validate_members(
            _zip_bytes({"a.txt": b"0123456789", "b.txt": b"0123456789"}),
            limits=limits,
        )


def test_rejects_high_compression_ratio() -> None:
    zeros = b"\x00" * 5_000
    info = zipfile.ZipInfo("zeros.bin")
    info.compress_type = zipfile.ZIP_DEFLATED
    packed = _zip_with_infos([(info, zeros)])
    limits = ArchiveLimits(
        max_upload_bytes=1024 * 1024,
        max_file_count=10,
        max_file_bytes=50_000,
        max_extracted_bytes=50_000,
        max_compression_ratio=2.0,
    )
    with pytest.raises(RejectedArchiveError):
        validate_members(packed, limits=limits)


def test_accepts_safe_relative_files() -> None:
    validate_members(
        _zip_bytes({"src/app.py": b"print(1)\n", "README.md": b"ok\n"}),
        limits=_LIMITS,
    )


def test_bounded_read_rejects_payload_over_budget() -> None:
    content = _zip_bytes({"blob.bin": b"x" * 200})
    with zipfile.ZipFile(io.BytesIO(content)) as archive:
        info = archive.infolist()[0]
        with pytest.raises(RejectedArchiveError, match="per-file size"):
            read_member_bounded(archive, info, max_bytes=50)


def test_bounded_read_returns_member_within_budget() -> None:
    content = _zip_bytes({"app.py": b"print(1)\n"})
    with zipfile.ZipFile(io.BytesIO(content)) as archive:
        info = archive.infolist()[0]
        assert read_member_bounded(archive, info, max_bytes=100) == b"print(1)\n"
