from typing import Any, Protocol

from src.domain.inventory import Inventory


class InventoryRepository(Protocol):
    def load(self) -> Inventory:
        ...

    def load_for_update(self, ingredient_names: list[str]) -> Inventory:
        ...

    def save(self, inventory: Inventory) -> None:
        ...

    def find_histories(
        self,
        ingredient_name: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[Any]:
        ...