from abc import ABC, abstractmethod

from src.domain.inventory import Inventory


class InventoryRepository(ABC):
    @abstractmethod
    def load(self) -> Inventory:
        """현재 재고를 조회한다."""
        raise NotImplementedError

    @abstractmethod
    def save(self, inventory: Inventory) -> None:
        """재고 상태를 저장한다."""
        raise NotImplementedError