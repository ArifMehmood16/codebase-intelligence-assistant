"""Domain model for fixture inventory items."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class InventoryItem:
    name: str
    quantity: int

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("name is required")
        if self.quantity < 0:
            raise ValueError("quantity cannot be negative")
