import pytest

from src.domain.quantity import Quantity
from src.domain.ingredient import Ingredient
from src.domain.inventory_item import InventoryItem


class TestInventoryItemValidation:
    
    def test_inventory_item_ingredient_must_be_ingredient(self):
        with pytest.raises(TypeError):
            InventoryItem(
                ingredient="원두",
                quantity=Quantity(1000),
            )

    def test_inventory_item_quantity_must_be_quantity(self):
        with pytest.raises(TypeError):
            InventoryItem(
                ingredient=Ingredient("원두"),
                quantity=1000,
            )

    def test_decrease_inventory_item(self):
        inventory_item = InventoryItem(
            ingredient=Ingredient("원두"),
            quantity=Quantity(1000),
        )

        inventory_item.decrease(Quantity(17))

        assert inventory_item.quantity == Quantity(983)

    def test_inventory_item_cannot_be_negative(self):
        inventory_item = InventoryItem(
            ingredient=Ingredient("원두"),
            quantity=Quantity(10),
        )

        with pytest.raises(ValueError):
            inventory_item.decrease(Quantity(11))

    def test_increase_inventory_item(self):
        inventory_item = InventoryItem(
            ingredient=Ingredient("원두"),
            quantity=Quantity(1000),
        )

        inventory_item.increase(Quantity(50))

        assert inventory_item.quantity == Quantity(1050)

    def test_error_to_increase_not_quantity(self):
        inventory_item = InventoryItem(
                ingredient=Ingredient("원두"),
                quantity=Quantity(1000),
            )
        with pytest.raises(TypeError):
            inventory_item.increase(50)