from abc import ABC, abstractmethod
from typing import Any


class AbstractUnitOfWork(ABC):
    menus: Any
    inventories: Any
    orders: Any

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