from dataclasses import dataclass
from typing import Union

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

    def multiply(self, multipler: Union[int, "Quantity"]) -> "Quantity":
        if isinstance(multipler, Quantity):
            factor = multipler.value
        elif isinstance(multipler, int):
            factor = multipler
        else:
            raise TypeError("multiplier는 int 또는 Quantity 타입이어야 합니다.")
        
        result = self.value * factor

        if result < 0:
            raise ValueError("Quantity는 음수가 될 수 없다.")

        return Quantity(result)
    
    def is_greater_than(self, other:"Quantity") -> bool:
        return self.value > other.value
    