import pytest

from src.domain.ingredient import Ingredient
def test_create_ingredient():
    ingredient = Ingredient(name="원두")

    assert ingredient.name == "원두"

def test_empty_ingredient_name_raises_value_error():
    with pytest.raises(ValueError):
        Ingredient(name="")

def test_blank_ingredient_name_raises_value_error():
    with pytest.raises(ValueError):
        Ingredient(name="   ")

def test_ingredient_name_must_be_string():
    with pytest.raises(TypeError):
        Ingredient(name=123)