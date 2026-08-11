from src.domain.ingredient import Ingredient
from src.domain.money import Money
from src.domain.quantity import Quantity
from src.infrastructure.models import (
    IngredientModel,
    InventoryItemModel,
    MenuModel,
)


def test_ingredient_model_creation():
    model = IngredientModel(name="원두", unit="g")
    assert model.name == "원두"
    assert model.unit == "g"


def test_menu_model_to_domain_mapping():
    model = MenuModel(name="아메리카노", price=3000)

    # ORM 속성이 Domain VO와 올바르게 대응되는지 검증
    assert model.name == "아메리카노"
    assert Money(model.price) == Money(3000)


def test_inventory_item_model_quantity_mapping():
    ing_model = IngredientModel(name="원두", unit="g")
    inv_model = InventoryItemModel(ingredient=ing_model, quantity=1000)

    assert inv_model.quantity == 1000
    assert Quantity(inv_model.quantity) == Quantity(1000)
    assert Ingredient(inv_model.ingredient.name, inv_model.ingredient.unit) == Ingredient("원두", "g")