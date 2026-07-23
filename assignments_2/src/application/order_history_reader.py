from typing import Protocol

from src.domain.order_record import OrderRecord


class OrderHistoryReader(Protocol):
    def find_today(self) -> list[OrderRecord]:
        """오늘 저장된 주문 이력을 조회한다."""
        ...