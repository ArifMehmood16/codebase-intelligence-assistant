"""HTTP controller for fixture inventory requests."""

from __future__ import annotations

from src.services.inventory import InventoryService


class ItemController:
    """Controller entry for inventory requests. There is no database layer."""

    def __init__(self, service: InventoryService) -> None:
        self._service = service

    def get_items(self) -> object:
        """GET /items — controllers call InventoryService, which stores items in memory."""
        return self._service.list_items()
