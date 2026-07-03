import pytest

from src.domain.inventory import Inventory
from src.domain.quantity import Quantity
from src.domain.ingredient import Ingredient
from src.domain.inventory_item import InventoryItem

def test_create_inventory():
    bean = Ingredient("원두")
    water = Ingredient("물")

    inventory = Inventory(
        items=[
            InventoryItem(bean, Quantity(170)),
            InventoryItem(water, Quantity(2500)),
        ]
    )

    assert len(inventory.items) == 2

def test_inventory_items_must_be_list():
    with pytest.raises(TypeError):
        Inventory(
            items="inventory"
        )

def test_inventory_items_must_contain_inventory_item():
    with pytest.raises(TypeError):
        Inventory(
            items=[
                "원두"
            ]
        )

def test_inventory_cannot_have_duplicate_ingredient():
    bean = Ingredient("원두")

    with pytest.raises(ValueError):
        Inventory(
            items=[
                InventoryItem(bean, Quantity(108)),
                InventoryItem(bean, Quantity(200)),
            ]
        )