"""Read an admitted ZIP into accepted source and ignored-member counts."""

from __future__ import annotations

import tempfile
import zipfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from codebase_assistant.ingestion.admission import admit_archive
from codebase_assistant.ingestion.errors import RejectedArchiveError
from codebase_assistant.ingestion.limits import ArchiveLimits
from codebase_assistant.ingestion.members import read_member_bounded, validate_members
from codebase_assistant.ingestion.source_policy import classify_source_file


@dataclass(frozen=True, slots=True)
class AcceptedMember:
    relative_path: str
    text: str


@dataclass(frozen=True, slots=True)
class IgnoredMember:
    relative_path: str
    reason: str


@dataclass(frozen=True, slots=True)
class ArchiveSummary:
    accepted: tuple[AcceptedMember, ...]
    ignored: tuple[IgnoredMember, ...]

    @property
    def indexed_file_count(self) -> int:
        return len(self.accepted)

    @property
    def ignored_file_count(self) -> int:
        return len(self.ignored)

    @property
    def ignored_reason_counts(self) -> tuple[tuple[str, int], ...]:
        counts = Counter(member.reason for member in self.ignored)
        return tuple(sorted(counts.items()))


def summarise_archive(
    content: bytes,
    filename: str,
    limits: ArchiveLimits,
    *,
    work_dir: Path | None = None,
) -> ArchiveSummary:
    with tempfile.TemporaryDirectory(prefix="ingest-", dir=work_dir) as raw:
        archive_path = Path(raw) / "upload.zip"
        archive_path.write_bytes(content)
        admit_archive(content, filename, limits)
        validate_members(content, limits)
        return _read_members(archive_path, limits)


def _read_members(archive_path: Path, limits: ArchiveLimits) -> ArchiveSummary:
    accepted: list[AcceptedMember] = []
    ignored: list[IgnoredMember] = []
    remaining = limits.max_extracted_bytes
    try:
        with zipfile.ZipFile(archive_path) as archive:
            for info in archive.infolist():
                if info.is_dir():
                    continue
                budget = min(limits.max_file_bytes, remaining)
                data = read_member_bounded(archive, info, budget)
                remaining -= len(data)
                compressed = info.compress_size
                inflated_ratio = 0.0 if compressed == 0 else len(data) / compressed
                if inflated_ratio > limits.max_compression_ratio:
                    raise RejectedArchiveError("compression ratio exceeds limit")
                decision = classify_source_file(info.filename, data)
                if decision.accepted and decision.text is not None:
                    accepted.append(
                        AcceptedMember(
                            relative_path=decision.relative_path,
                            text=decision.text,
                        )
                    )
                else:
                    ignored.append(
                        IgnoredMember(
                            relative_path=decision.relative_path,
                            reason=decision.reason,
                        )
                    )
    except zipfile.BadZipFile as exc:
        raise RejectedArchiveError("archive is malformed") from exc
    accepted.sort(key=lambda member: member.relative_path)
    ignored.sort(key=lambda member: member.relative_path)
    return ArchiveSummary(accepted=tuple(accepted), ignored=tuple(ignored))
