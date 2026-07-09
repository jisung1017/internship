import pytest

from src.domain.quantity import Quantity
from src.domain.ingredient import Ingredient
from src.domain.recipe_item import RecipeItem


class TestRecipeItemValidation:
    
    def test_recipe_item_ingredient_must_be_ingredient(self):
        with pytest.raises(TypeError):
            RecipeItem(
                ingredient = "원두",
                quantity=Quantity(18), 
            )

    def test_recipe_item_quantity_must_be_ingredient(self):
        with pytest.raises(TypeError):
            RecipeItem(
                ingredient = Ingredient(name="원두"),
                quantity= 18, 
            )