from src.domain.exceptions import PaymentFailedError
from src.domain.order import Order


class Payment:
    """결제 승인을 담당하는 도메인 객체 (PG 승인 가상화)"""

    def __init__(self, is_approved: bool = True):
        self.is_approved = is_approved

    def pay(self, order: Order) -> None:
        if not self.is_approved:
            raise PaymentFailedError("카드 승인 거절 또는 결제에 실패했습니다.")