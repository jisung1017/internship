import pytest

from src.domain.quantity import Quantity
from src.domain.ingredient import Ingredient
from src.domain.inventory_item import InventoryItem

def test_create_inventory_item():
    ingredient = Ingredient("원두")

    inventory_item = InventoryItem(
        ingredient=ingredient,
        quantity=Quantity(1000),
    )

    assert inventory_item.ingredient == ingredient
    assert inventory_item.quantity == Quantity(1000)

def test_inventory_item_ingredient_must_be_ingredient():
    with pytest.raises(TypeError):
        InventoryItem(
            ingredient="원두",
            quantity=Quantity(1000),
        )

def test_inventory_item_quantity_must_be_quantity():
    with pytest.raises(TypeError):
        InventoryItem(
            ingredient=Ingredient("원두"),
            quantity=1000,
        )

def test_decrease_inventory_item():
    inventory_item = InventoryItem(
        ingredient=Ingredient("원두"),
        quantity=Quantity(1000),
    )

    inventory_item.decrease(Quantity(17))

    assert inventory_item.quantity == Quantity(983)

def test_inventory_item_cannot_be_negative():
    inventory_item = InventoryItem(
        ingredient=Ingredient("원두"),
        quantity=Quantity(10),
    )

    with pytest.raises(ValueError):
        inventory_item.decrease(Quantity(11))