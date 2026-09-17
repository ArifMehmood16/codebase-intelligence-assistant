"""HTTP-style handlers for the fixture inventory API endpoints."""

from __future__ import annotations

from src.models.item import InventoryItem
from src.services.inventory import InventoryService


def list_items(service: InventoryService, *, limit: int = 20) -> list[InventoryItem]:
    """Return a page of inventory items for GET /items."""
    return service.list_items(limit=limit)


def create_item(
    service: InventoryService,
    *,
    name: str,
    quantity: int,
) -> InventoryItem:
    """Validate input and create an item for POST /items."""
    cleaned = name.strip()
    if not cleaned:
        raise ValueError("item name is required")
    if quantity < 0:
        raise ValueError("quantity cannot be negative")
    return service.create_item(name=cleaned, quantity=quantity)
