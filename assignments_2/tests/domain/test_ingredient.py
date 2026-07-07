import pytest

from src.domain.ingredient import Ingredient

class TestIngredientCreate:

    def test_create_ingredient(self):
        ingredient = Ingredient(name="원두")

        assert ingredient.name == "원두"

    def test_create_ingredient_with_gap(self):
        ingredient = Ingredient(name="  원두  ")

        assert ingredient.name == "원두"

class TestIngredientValidation:
    def test_empty_ingredient_name_raises_value_error(self):
        with pytest.raises(ValueError):
            Ingredient(name="")

    def test_blank_ingredient_name_raises_value_error(self):
        with pytest.raises(ValueError):
            Ingredient(name="   ")

    def test_ingredient_name_must_be_string(self):
        with pytest.raises(TypeError):
            Ingredient(name=123)