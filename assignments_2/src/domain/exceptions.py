class InsufficientBalanceError(Exception):
    """잔액이 부족합니다."""

class OutOfStockError(Exception):
    """재고가 부족합니다."""

class PaymentFailedError(Exception):
    """결제 승인 실패 예외"""