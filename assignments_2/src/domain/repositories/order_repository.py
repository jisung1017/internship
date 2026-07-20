from abc import ABC, abstractmethod

from src.domain.order import Order


class OrderRepository(ABC):
    @abstractmethod
    def save(self, order: Order) -> None:
        """주문을 저장한다."""
        raise NotImplementedError