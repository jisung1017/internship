from abc import ABC, abstractmethod
from typing import Any

from src.application.inventory_repository import InventoryRepository
from src.application.menu_repository import MenuRepository
from src.application.order_repository import OrderRepository

class AbstractUnitOfWork(ABC):
    menus: MenuRepository
    inventories: InventoryRepository
    orders: OrderRepository

    def __enter__(self) -> "AbstractUnitOfWork":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if exc_type is not None:
            self.rollback()

    @abstractmethod
    def commit(self) -> None:
        """트랜잭션을 커밋합니다."""
        raise NotImplementedError

    @abstractmethod
    def rollback(self) -> None:
        """트랜잭션을 롤백합니다."""
        raise NotImplementedError