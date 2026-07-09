from dataclasses import dataclass


@dataclass(frozen=True)
class Option:
    id: int
    name: str
    price: int
    amount: int

    def total_cost(self):
        return self.price * self.amount
