"""One-off seed script. Not part of the runtime request path."""

from __future__ import annotations

from src.services.inventory import InventoryService


def main() -> None:
    service = InventoryService()
    service.create_item(name="demo-widget", quantity=3)
    service.create_item(name="demo-gadget", quantity=1)
    print(f"seeded {len(service.list_items())} items")


if __name__ == "__main__":
    main()
