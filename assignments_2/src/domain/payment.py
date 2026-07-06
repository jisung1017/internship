from src.domain.money import Money
from src.domain.order import Order
from src.domain.exceptions import InsufficientBalanceError

class Payment:
    def __init__(self, balance: Money):
        if not isinstance(balance, Money):
            raise TypeError("잔액은 Money 타입입니다.")

        if balance.amount < 0:
            raise ValueError("잔액은 음수가 될 수 없습니다.")

        self.balance = balance
        self._is_paid = False

    @property
    def is_paid(self) -> bool:
        return self._is_paid

    def pay(self, order: Order) -> None:
        if not isinstance(order, Order):
            raise TypeError("order 는 Order 타입입니다.")

        if self._is_paid:
            raise ValueError("결제가 이미 완료되었습니다.")

        total_price = order.total_price()

        if self.balance < total_price:
            raise InsufficientBalanceError()

        self.balance = self.balance.subtract(total_price)
        self._is_paid = True