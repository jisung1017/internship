import pytest

from src.domain.recipe import Recipe
from src.domain.quantity import Quantity
from src.domain.ingredient import Ingredient
from src.domain.recipe_item import RecipeItem

def test_create_recipe():
    bean = Ingredient("원두")
    water = Ingredient("물")

    recipe = Recipe(
        items=[
            RecipeItem(bean, Quantity(17)),
            RecipeItem(water, Quantity(250)),
        ]
    )

    assert len(recipe.items) == 2

def test_recipe_items_must_be_list():
    with pytest.raises(TypeError):
        Recipe(
            items="recipe"
        )

def test_recipe_items_must_contain_recipe_item():
    with pytest.raises(TypeError):
        Recipe(
            items=[
                "원두"
            ]
        )

def test_recipe_cannot_have_duplicate_ingredient():
    bean = Ingredient("원두")

    with pytest.raises(ValueError):
        Recipe(
            items=[
                RecipeItem(bean, Quantity(18)),
                RecipeItem(bean, Quantity(20)),
            ]
        )