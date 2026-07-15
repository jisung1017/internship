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

        inventory._consume(recipe, Quantity(1))

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
            inventory._consume(recipe, Quantity(1))


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


class TestInventoryCanConsumeAll:

    def test_can_consume_all_returns_false_when_shared_ingredient_insufficient(self):
        inventory = Inventory(
            items=[InventoryItem(Ingredient("원두"), Quantity(50))]
        )

        recipe = Recipe(items=[RecipeItem(Ingredient("원두"), Quantity(18))])

        requirements = [(recipe, Quantity(2)), (recipe, Quantity(1))]

        # 총 50개 - 합산 54개 -> False
        assert inventory.can_consume_all(requirements) is False

    def test_can_consume_all_returns_true_when_sufficient(self):
        inventory = Inventory(
            items=[InventoryItem(Ingredient("원두"), Quantity(100))]
        )

        recipe = Recipe(items=[RecipeItem(Ingredient("원두"), Quantity(18))])

        requirements = [(recipe, Quantity(2)), (recipe, Quantity(1))]

        # 총 50개 - 합산 54개 -> True
        assert inventory.can_consume_all(requirements) is True


class TestInventoryConsumeAll:

    def test_consume_all_decreases_shared_ingredient_correctly(self):
        inventory = Inventory(
            items=[InventoryItem(Ingredient("원두"), Quantity(100))]
        )

        americano_recipe = Recipe(items=[RecipeItem(Ingredient("원두"), Quantity(18))])
        latte_recipe = Recipe(items=[RecipeItem(Ingredient("원두"), Quantity(18))])

        requirements = [
            (americano_recipe, Quantity(2)),
            (latte_recipe, Quantity(1)),
        ]

        inventory.consume_all(requirements)

        assert inventory.items[0].quantity == Quantity(46)  # 100 - 54

    def test_consume_all_raises_out_of_stock_when_missing_ingredient(self):
        inventory = Inventory(
            items=[InventoryItem(Ingredient("원두"), Quantity(100))]
        )

        recipe = Recipe(items=[RecipeItem(Ingredient("우유"), Quantity(200))])

        with pytest.raises(OutOfStockError):
            inventory.consume_all([(recipe, Quantity(1))])


class TestInventoryRestock:

    def test_restock_increases_existing_ingredient(self):
        inventory = create_inventory()

        inventory.restock(Ingredient("원두"), Quantity(100))

        assert inventory.get_quantity(Ingredient("원두")) == Quantity(270)

    def test_restock_zero_raises_value_error(self):
        inventory = create_inventory()

        with pytest.raises(ValueError):
            inventory.restock(Ingredient("원두"), Quantity(0))

    def test_restock_records_history(self):
        inventory = create_inventory()

        inventory.restock(Ingredient("원두"), Quantity(100))

        assert len(inventory.history) == 1
        assert inventory.history[0].change == 100
        assert inventory.history[0].reason == "RESTOCK"

    def test_consume_records_history(self):
        inventory = create_inventory()
        recipe = Recipe(items=[RecipeItem(Ingredient("원두"), Quantity(17))])

        inventory._consume(recipe, Quantity(1))

        assert len(inventory.history) == 1
        assert inventory.history[0].change == -17
        assert inventory.history[0].reason == "CONSUME"


    def get_quantity(inventory: Inventory, ingredient: Ingredient) -> Quantity:
        for item in inventory.items:
            if item.ingredient == ingredient:
                return item.quantity
        raise AssertionError("재고를 찾을 수 없습니다.")