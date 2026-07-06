class InsufficientBalanceError(Exception):
    """잔액이 부족합니다."""

class OutOfStockError(Exception):
    """재고가 부족합니다."""