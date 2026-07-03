from dataclasses import dataclass

@dataclass(frozen=True)
class Quantity:
    value: int

    def __post_init__(self):
        if type(self.value) is not int:
            raise TypeError("Quantity는 integer 타입이어야 한다.")
        
        if self.value < 0:
            raise ValueError("Quantity는 음수가 될 수 없다.")
    
    def add(self, other: "Quantity") -> "Quantity":
        return Quantity(self.value + other.value)
    
    def subtract(self, other: "Quantity") -> "Quantity":
        result = self.value - other.value

        if result < 0:
            raise ValueError("Quantity는 음수가 될 수 없다.")
        
        return Quantity(result)

    def multiply(self, multipler:int) -> "Quantity":
        result = self.value * multipler

        if result < 0:
            raise ValueError("Quantity는 음수가 될 수 없다.")

        return Quantity(result)
    
    def is_greater_than(self, other:"Quantity") -> bool:
        return self.value > other.value
    