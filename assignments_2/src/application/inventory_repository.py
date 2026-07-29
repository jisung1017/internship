from typing import Protocol

from src.domain.inventory import Inventory


class InventoryRepository(Protocol):
    def load(self) -> Inventory:
        ...

    def load_for_update(self, ingredient_names: list[str]) -> Inventory:
        ...

    def save(self, inventory: Inventory) -> None:
        ...