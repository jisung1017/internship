import pytest

from src.domain.ingredient import Ingredient
from src.domain.quantity import Quantity

def test_create_ingredient():
    ingredient = Ingredient(
        name="원두",
        quantity = Quantity(17),
    )

    assert ingredient.name == "원두"
    assert ingredient.quantity == Quantity(17)