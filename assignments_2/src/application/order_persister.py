from typing import Protocol

from src.domain.inventory import Inventory
from src.domain.order import Order


class OrderPersister(Protocol):
    def persist(self, order: Order, inventory: Inventory) -> None:
        """주문 이력과 재고 변경을 하나의 트랜잭션으로 저장한다 (커밋까지 책임)."""
        ...