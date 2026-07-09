import pytest

from src.domain.money import Money
from src.domain.quantity import Quantity
from src.domain.menu import Menu
from src.domain.option_group import OptionGroup
from src.domain.option import Option
from src.domain.recipe import Recipe
from src.domain.recipe_item import RecipeItem
from src.domain.ingredient import Ingredient


@pytest.fixture
def hot_option():
    return Option(name="HOT", additional_price=Money(0))

@pytest.fixture
def ice_option():
    return Option(name="ICE", additional_price=Money(0))

@pytest.fixture
def shot_option():
    return Option(name="샷 추가", additional_price=Money(500))

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
def temperature_group(hot_option, ice_option) -> OptionGroup:
    return OptionGroup(
        name="온도",
        min_quantity=Quantity(1),
        max_quantity=Quantity(1),
        options=[hot_option, ice_option],
    )

@pytest.fixture
def shot_group(shot_option) -> OptionGroup:
    return OptionGroup(
        name="샷",
        min_quantity=Quantity(0),
        max_quantity=Quantity(3),
        options=[shot_option],
    )

@pytest.fixture
def americano(create_recipe, temperature_group, shot_group):
    return Menu(
        name="아메리카노",
        price=Money(3000),
        recipe=create_recipe,
        option_groups=[temperature_group, shot_group],
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
        
    def test_option_groups_must_be_list(self, create_recipe, temperature_group, shot_group):
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


class TestMenuOptionValidation:

    def test_validate_passes_with_valid_selection(self, americano, hot_option):
        americano.validate_selected_options([hot_option])

    def test_validate_passes_with_repeated_option(self, americano, hot_option, shot_option):
        americano.validate_selected_options([hot_option, shot_option, shot_option])

    def test_validate_raises_when_required_group_not_selected(self, americano):
        with pytest.raises(ValueError):
            americano.validate_selected_options([])

    def test_validate_raises_when_group_exceeds_max(self, americano, hot_option, shot_option):
        with pytest.raises(ValueError):
            americano.validate_selected_options([hot_option] + [shot_option] * 5)

    def test_validate_raises_when_option_not_in_menu(self, americano, hot_option):
        syrup = Option(name="시럽 추가", additional_price=Money(300))

        with pytest.raises(ValueError):
            americano.validate_selected_options([hot_option, syrup])

    def test_validate_raises_when_two_different_options_selected_in_single_choice_group(
        self, americano, hot_option, ice_option
    ):
        """온도(min=1,max=1) 그룹에서 HOT과 ICE를 동시에 선택하면 안 된다."""
        with pytest.raises(ValueError):
            americano.validate_selected_options([hot_option, ice_option])