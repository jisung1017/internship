import pytest

from src.domain.exceptions import OutOfStockError
from src.domain.ingredient import Ingredient
from src.domain.inventory import Inventory
from src.domain.inventory_item import InventoryItem
from src.domain.quantity import Quantity
from src.domain.recipe import Recipe
from src.domain.recipe_item import RecipeItem


def create_inventory() -> Inventory:
    return Inventory(
        items=[
            InventoryItem(Ingredient("원두"), Quantity(170)),
            InventoryItem(Ingredient("물"), Quantity(2500)),
        ]
    )


class TestInventoryValidation:
    def test_create_inventory(self):
        inventory = create_inventory()

        assert len(inventory.items) == 2

    def test_inventory_items_must_be_list(self):
        with pytest.raises(TypeError):
            Inventory(items="inventory")

    def test_inventory_items_must_contain_inventory_item(self):
        with pytest.raises(TypeError):
            Inventory(
                items=[
                    "원두",
                ]
            )

    def test_inventory_cannot_have_duplicate_ingredient(self):
        bean = Ingredient("원두")

        with pytest.raises(ValueError):
            Inventory(
                items=[
                    InventoryItem(bean, Quantity(108)),
                    InventoryItem(bean, Quantity(200)),
                ]
            )


class TestInventoryBehavior:
    def test_consume_recipe(self):
        inventory = create_inventory()

        recipe = Recipe(
            items=[
                RecipeItem(Ingredient("원두"), Quantity(17)),
                RecipeItem(Ingredient("물"), Quantity(250)),
            ]
        )

        inventory.consume(recipe, Quantity(1))

        assert inventory.items[0].quantity == Quantity(153)
        assert inventory.items[1].quantity == Quantity(2250)

    def test_consume_recipe_with_missing_ingredient_raises_out_of_stock_error(self):
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
            inventory.consume(recipe, Quantity(1))


class TestInventoryCanConsume:
    def test_can_consume_returns_true_when_quantity_equals_required(self):
        inventory = Inventory(
            items=[
                InventoryItem(Ingredient("원두"), Quantity(34)),
            ]
        )

        recipe = Recipe(
            items=[
                RecipeItem(Ingredient("원두"), Quantity(17)),
            ]
        )

        assert inventory.can_consume(recipe, Quantity(2)) is True

    def test_can_consume_returns_true_when_inventory_is_sufficient(self):
        inventory = create_inventory()

        recipe = Recipe(
            items=[
                RecipeItem(Ingredient("원두"), Quantity(17)),
                RecipeItem(Ingredient("물"), Quantity(250)),
            ]
        )

        assert inventory.can_consume(recipe, Quantity(2)) is True

    def test_can_consume_returns_false_when_inventory_is_insufficient(self):
        inventory = Inventory(
            items=[
                InventoryItem(Ingredient("원두"), Quantity(10)),
            ]
        )

        recipe = Recipe(
            items=[
                RecipeItem(Ingredient("원두"), Quantity(17)),
            ]
        )

        assert inventory.can_consume(recipe, Quantity(2)) is False

    def test_can_consume_returns_false_when_ingredient_is_missing(self):
        inventory = Inventory(
            items=[
                InventoryItem(Ingredient("원두"), Quantity(100)),
            ]
        )

        recipe = Recipe(
            items=[
                RecipeItem(Ingredient("우유"), Quantity(200)),
            ]
        )

        assert inventory.can_consume(recipe, Quantity(2)) is False