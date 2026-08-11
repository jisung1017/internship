import pytest
from src.application.pending_order import PendingOrder
from src.domain.ingredient import Ingredient
from src.domain.menu import Menu
from src.domain.money import Money
from src.domain.option import Option
from src.domain.option_group import OptionGroup
from src.domain.option_item import OptionItem
from src.domain.quantity import Quantity
from src.domain.recipe import Recipe
from src.domain.recipe_item import RecipeItem


def build_americano() -> Menu:
    bean = Ingredient("원두")
    temperature_option = Option(
        name="온도",
        default_min=Quantity(1),
        default_max=Quantity(1),
        selection_mode="choice",
        items=[
            OptionItem(name="HOT", additional_price=Money(0)),
            OptionItem(name="ICE", additional_price=Money(0)),
        ],
    )
    shot_option = Option(
        name="샷 추가",
        default_min=Quantity(0),
        default_max=Quantity(4),
        selection_mode="count",
        items=[
            OptionItem(name="샷 추가", additional_price=Money(500)),
        ],
    )
    return Menu(
        name="아메리카노",
        price=Money(3000),
        recipe=Recipe(items=[RecipeItem(bean, Quantity(18))]),
        option_groups=[
            OptionGroup(option=temperature_option),
            OptionGroup(option=shot_option),
        ],
    )


def build_menu_without_options() -> Menu:
    bean = Ingredient("원두")
    return Menu(
        name="에스프레소",
        price=Money(3500),
        recipe=Recipe(items=[RecipeItem(bean, Quantity(10))]),
        option_groups=[],
    )


class TestPendingOrderOptionProgress:
    def test_current_option_group_returns_first_group_initially(self):
        pending = PendingOrder(menu=build_americano())
        assert pending.current_option_group().name == "온도"

    def test_current_option_group_returns_none_when_no_option_groups(self):
        pending = PendingOrder(menu=build_menu_without_options())
        assert pending.current_option_group() is None
        assert pending.is_option_selection_done() is True

    def test_select_current_option_group_advances_to_next_group(self):
        menu = build_americano()
        pending = PendingOrder(menu=menu)
        hot = menu.option_groups[0].options[0]
        pending.select_current_option_group([hot])
        assert pending.current_option_group().name == "샷 추가"
        assert pending.selected_options == [hot]

    def test_select_current_option_group_marks_done_after_last_group(self):
        menu = build_americano()
        pending = PendingOrder(menu=menu)
        hot = menu.option_groups[0].options[0]
        pending.select_current_option_group([hot])
        pending.select_current_option_group([])
        assert pending.is_option_selection_done() is True

    def test_select_current_option_group_raises_when_already_done(self):
        pending = PendingOrder(menu=build_menu_without_options())
        with pytest.raises(ValueError):
            pending.select_current_option_group([])


class TestPendingOrderQuantity:
    def test_set_quantity_within_range(self):
        pending = PendingOrder(menu=build_menu_without_options())
        pending.set_quantity(Quantity(3))
        assert pending.quantity == Quantity(3)

    def test_set_quantity_below_min_raises_value_error(self):
        pending = PendingOrder(menu=build_menu_without_options())
        with pytest.raises(ValueError):
            pending.set_quantity(Quantity(0))

    def test_set_quantity_above_max_raises_value_error(self):
        pending = PendingOrder(menu=build_menu_without_options())
        with pytest.raises(ValueError):
            pending.set_quantity(Quantity(11))


class TestPendingOrderReady:
    def test_is_ready_false_when_quantity_not_set(self):
        pending = PendingOrder(menu=build_menu_without_options())
        assert pending.is_ready() is False

    def test_is_ready_false_when_option_selection_not_done(self):
        pending = PendingOrder(menu=build_americano())
        pending.set_quantity(Quantity(1))
        assert pending.is_ready() is False

    def test_is_ready_true_when_options_done_and_quantity_set(self):
        pending = PendingOrder(menu=build_menu_without_options())
        pending.set_quantity(Quantity(1))
        assert pending.is_ready() is True