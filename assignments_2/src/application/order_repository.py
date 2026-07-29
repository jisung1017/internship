from typing import Protocol

from src.domain.order import Order
from src.domain.order_record import OrderRecord


class OrderRepository(Protocol):
    def save(self, order: Order) -> None:
        ...

    def find_today(self) -> list[OrderRecord]:
        ...