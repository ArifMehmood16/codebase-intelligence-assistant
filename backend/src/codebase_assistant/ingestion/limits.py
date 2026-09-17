from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ArchiveLimits:
    max_upload_bytes: int
    max_file_count: int = 500
    max_file_bytes: int = 1_048_576
    max_extracted_bytes: int = 20_971_520
    max_compression_ratio: float = 100.0
