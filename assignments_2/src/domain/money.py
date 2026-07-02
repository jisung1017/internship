from dataclasses import dataclass

@dataclass(frozen=True)
class Money:
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

    def multiply(self, multipler:int) -> "Money":
        result = self.amount * multipler

        if result < 0:
            raise ValueError("Money는 음수가 될 수 없다.")

        return Money(result)