"""Inventory service used by the fixture API handlers."""

from __future__ import annotations

from src.models.item import InventoryItem


class InventoryService:
    def __init__(self) -> None:
        self._items: list[InventoryItem] = []

    def list_items(self, *, limit: int = 20) -> list[InventoryItem]:
        if limit < 1:
            return []
        return list(self._items[:limit])

    def create_item(self, *, name: str, quantity: int) -> InventoryItem:
        item = InventoryItem(name=name, quantity=quantity)
        self._items.append(item)
        return item

    def find_by_name(self, name: str) -> InventoryItem | None:
        needle = name.strip().lower()
        for item in self._items:
            if item.name.lower() == needle:
                return item
        return None
