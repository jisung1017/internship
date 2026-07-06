import pytest

from src.domain.inventory import Inventory
from src.domain.quantity import Quantity
from src.domain.ingredient import Ingredient
from src.domain.inventory_item import InventoryItem
from src.domain.recipe import Recipe
from src.domain.recipe_item import RecipeItem
from src.domain.exceptions import OutOfStockError

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

def test_inventory_consume():
    inventory = Inventory(
        items=[
            InventoryItem(Ingredient("원두"), Quantity(170)),
            InventoryItem(Ingredient("물"), Quantity(2500)),
        ]
    )

    recipe = Recipe(
        items=[
            RecipeItem(Ingredient("원두"), Quantity(17)),
            RecipeItem(Ingredient("물"), Quantity(250)),
        ]
    )

    inventory.consume(recipe)

    assert inventory.items[0].quantity == Quantity(153)
    assert inventory.items[1].quantity == Quantity(2250)
    
def test_consume_recipe_with_missing_ingredient_raises_value_error():
    bean = Ingredient("원두")
    milk = Ingredient("우유")

    inventory = Inventory(
        items=[
            InventoryItem(bean, Quantity(1000)),
        ]
    )

    recipe = Recipe(
        items=[
            RecipeItem(bean, Quantity(18)),
            RecipeItem(milk, Quantity(200)),
        ]
    )

    with pytest.raises(OutOfStockError):
        inventory.consume(recipe)