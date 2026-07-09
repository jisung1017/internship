from dataclasses import dataclass

from src.domain.ingredient import Ingredient
from src.domain.quantity import Quantity


@dataclass
class RecipeItem:
    ingredient: Ingredient
    quantity: Quantity

    def __post_init__(self) -> None:
        if not isinstance(self.ingredient, Ingredient):
            raise TypeError("ingredient는 Ingredient 타입이어야 합니다.")

        if not isinstance(self.quantity, Quantity):
            raise TypeError("quantity는 Quantity 타입이어야 합니다.")