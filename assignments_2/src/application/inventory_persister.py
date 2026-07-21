from typing import Protocol

from src.domain.inventory import Inventory


class InventoryPersister(Protocol):
    def persist(self, inventory: Inventory) -> None:
        """재고 변경을 즉시 영속화한다 (자체 트랜잭션으로 커밋까지 책임진다)."""
        ...