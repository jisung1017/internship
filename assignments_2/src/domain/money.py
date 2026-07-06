from dataclasses import dataclass

from src.domain.quantity import Quantity


@dataclass(frozen=True)
class Money:
    """
    Value Object

    dataclass(frozen=True)가 자동으로 제공하는 기능
    - __init__
    - __repr__
    - __eq__
    """
    amount: int

    def __post_init__(self):
        if type(self.amount) is not int:
            raise TypeError("Money는 integer 타입이어야 한다.")

        if self.amount < 0:
            raise ValueError("Money는 음수가 될 수 없다.")

    def add(self, other: "Money") -> "Money":
        return Money(self.amount + other.amount)

    def subtract(self, other: "Money") -> "Money":
        result = self.amount - other.amount

        if result < 0:
            raise ValueError("Money는 음수가 될 수 없다.")

        return Money(result)

    def multiply(self, multiplier: Quantity) -> "Money":
        if type(multiplier) is not Quantity:
            raise TypeError("Multiplier는 Quantity 타입이어야 합니다.")

        return Money(self.amount * multiplier.value)

    def __lt__(self, other: "Money") -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount < other.amount

    def __le__(self, other: "Money") -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount <= other.amount

    def __gt__(self, other: "Money") -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount > other.amount

    def __ge__(self, other: "Money") -> bool:
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount >= other.amount