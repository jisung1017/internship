from src.domain.money import Money
from src.domain.order import Order


class Payment:
    def __init__(self, balance: Money):
        if not isinstance(balance, Money):
            raise TypeError("balance must be a Money")

        if balance.amount < 0:
            raise ValueError("balance cannot be negative")

        self.balance = balance
        self._is_paid = False

    @property
    def is_paid(self) -> bool:
        return self._is_paid

    def pay(self, order: Order) -> None:
        if not isinstance(order, Order):
            raise TypeError("order must be an Order")

        if self._is_paid:
            raise ValueError("payment has already been completed")

        total_price = order.total_price()

        if self.balance < total_price:
            raise ValueError("insufficient balance")

        self.balance = self.balance.subtract(total_price)
        self._is_paid = True