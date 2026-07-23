from abc import ABC, abstractmethod

from src.domain.order import Order
from src.domain.order_record import OrderRecord


class OrderRepository(ABC):
    @abstractmethod
    def save(self, order: Order) -> None:
        """주문을 저장한다."""
        raise NotImplementedError

    @abstractmethod
    def find_today(self) -> list[OrderRecord]:
        """오늘(자정 이후) 저장된 주문 이력을 조회한다."""
        raise NotImplementedError