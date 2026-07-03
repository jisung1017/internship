from dataclasses import dataclass

from src.domain.ingredient import Ingredient
from src.domain.quantity import Quantity

@dataclass
class InventoryItem:
    ingredient: Ingredient
    quantity: Quantity

    def __post_init__(self):
        if type(self.ingredient) is not Ingredient:
            raise TypeError("InventoryItem 의 ingredient 는 Ingredient 여야 한다.")
    
        if type(self.quantity) is not Quantity:
            raise TypeError("InventoryItem 의 quantity 는 Quantity 여야 한다.")
    
    def decrease(self, quantity: Quantity) -> None:
        self.quantity = self.quantity.subtract(quantity)