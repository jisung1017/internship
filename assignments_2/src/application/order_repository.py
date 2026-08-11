from typing import Protocol
from uuid import UUID

from src.domain.order import Order
from src.domain.order_record import OrderRecord


class OrderRepository(Protocol):
    """통합 주문 Repository 인터페이스"""

    def save(self, order: Order) -> None:
        ...

    def find_by_uuid(self, order_uuid: UUID) -> OrderRecord | None:
        ...

    def find_today(self) -> list[OrderRecord]:
        ...