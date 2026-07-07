import pytest

from src.domain.recipe import Recipe
from src.domain.quantity import Quantity
from src.domain.ingredient import Ingredient
from src.domain.recipe_item import RecipeItem


class TestRecipeValidation:
        
    def test_create_recipe(self):
        bean = Ingredient("원두")
        water = Ingredient("물")

        recipe = Recipe(
            items=[
                RecipeItem(bean, Quantity(17)),
                RecipeItem(water, Quantity(250)),
            ]
        )

        assert len(recipe.items) == 2

    def test_recipe_items_must_be_list(self):
        with pytest.raises(TypeError):
            Recipe(
                items="recipe"
            )

    def test_recipe_items_must_contain_recipe_item(self):
        with pytest.raises(TypeError):
            Recipe(
                items=[
                    "원두"
                ]
            )

    def test_recipe_cannot_have_duplicate_ingredient(self):
        bean = Ingredient("원두")

        with pytest.raises(ValueError):
            Recipe(
                items=[
                    RecipeItem(bean, Quantity(18)),
                    RecipeItem(bean, Quantity(20)),
                ]
            )