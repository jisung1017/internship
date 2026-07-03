import pytest

from src.domain.quantity import Quantity
from src.domain.ingredient import Ingredient
from src.domain.recipe_item import RecipeItem

def test_create_recipe_item():  
    recipe_item = RecipeItem(
        ingredient = Ingredient(name="원두"),
        quantity=Quantity(18),
    )

    assert recipe_item.ingredient == Ingredient(name="원두")
    assert recipe_item.quantity == Quantity(18)

def test_recipe_item_ingredient_must_be_ingredient():
    with pytest.raises(TypeError):
        RecipeItem(
            ingredient = "원두",
            quantity=Quantity(18), 
        )

def test_recipe_item_quantity_must_be_ingredient():
    with pytest.raises(TypeError):
        RecipeItem(
            ingredient = Ingredient(name="원두"),
            quantity= 18, 
        )
