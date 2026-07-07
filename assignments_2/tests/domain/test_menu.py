import pytest

from src.domain.money import Money
from src.domain.quantity import Quantity
from src.domain.menu import Menu
from src.domain.option_group import OptionGroup
from src.domain.recipe import Recipe
from src.domain.recipe_item import RecipeItem
from src.domain.ingredient import Ingredient


@pytest.fixture
def create_recipe() -> Recipe:
    return Recipe(
        items=[
            RecipeItem(
                ingredient=Ingredient("원두"),
                quantity=Quantity(18),
            )
        ]
    )

@pytest.fixture
def temperature_group() -> OptionGroup:
    return OptionGroup(
        name="온도",
        min_quantity=Quantity(1),
        max_quantity=Quantity(1),
    )

@pytest.fixture
def shot_group() -> OptionGroup:
    return OptionGroup(
        name="샷",
        min_quantity=Quantity(0),
        max_quantity=Quantity(3),
    )


class TestMenuValidation:

    def test_empty_menu_raises_value_error(self, create_recipe):
        with pytest.raises(ValueError):
            Menu(
                name= "",
                price = Money(3500),
                recipe=create_recipe,
            )

    def test_blank_menu_raises_value_error(self, create_recipe):
        with pytest.raises(ValueError):
            Menu(
                name= "   ",
                price = Money(3500),
                recipe=create_recipe,
            )

    def test_menu_must_be_string(self, create_recipe):
        with pytest.raises(TypeError):
            Menu(
                name= 1234,
                price = Money(3500),
                recipe=create_recipe,
            )

    def test_price_must_be_Money(self, create_recipe):
        with pytest.raises(TypeError):
            Menu(
                name= "아메리카노",
                price = 3500,               
                recipe=create_recipe,
            )

    def test_menu_name_is_required(self, create_recipe):
        with pytest.raises(TypeError):
            Menu(
                price = Money(3500),
                recipe=create_recipe,
            )
        
    def test_menu_price_is_required(self, create_recipe):
        with pytest.raises(TypeError):
            Menu(
                name = "아메리카노",
                recipe=create_recipe,
            )
        
    def test_option_groups_must_be_list(tself, create_recipe, temperature_group, shot_group):
        with pytest.raises(TypeError):
            Menu(
                name="아메리카노",
                price=Money(3000),
                recipe=create_recipe,
                option_groups=(temperature_group, shot_group),
            )
            
    def test_option_groups_must_be_option_in_list(self, create_recipe, shot_group):
        with pytest.raises(TypeError):
            Menu(
                name="아메리카노",
                price=Money(3000),
                recipe=create_recipe,
                option_groups=("temperature_group", shot_group),
            )

    def test_recipe_must_be_recipe(self):
        with pytest.raises(TypeError):
            Menu(
                name="아메리카노",
                price=Money(3500),
                recipe="recipe",
            )

    def test_recipe_is_required(self):
        with pytest.raises(TypeError):
            Menu(
                name="아메리카노",
                price=Money(3500),
            )