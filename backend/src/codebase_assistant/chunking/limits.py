from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ChunkingLimits:
    max_lines: int = 40
    overlap_lines: int = 8

    def __post_init__(self) -> None:
        if self.max_lines < 1:
            raise ValueError("max_lines must be at least 1")
        if self.overlap_lines < 0:
            raise ValueError("overlap_lines cannot be negative")
