import pytest

from src.domain.cart_item import CartItem
from src.domain.ingredient import Ingredient
from src.domain.menu import Menu
from src.domain.money import Money
from src.domain.option_item import OptionItem
from src.domain.quantity import Quantity
from src.domain.recipe import Recipe
from src.domain.recipe_item import RecipeItem


def create_recipe() -> Recipe:
    return Recipe(items=[RecipeItem(Ingredient("원두"), Quantity(18))])

def make_menu(
        name:str = "아메리카노",
        price:int = 3000
) -> Menu:
    return Menu(name=name, price=Money(price), recipe=create_recipe())

def make_option(
        name:str = "옵션",
        price:int = 500
) -> OptionItem:
    return OptionItem(name=name, additional_price=Money(price))


class TestCartItemValidation:

    def test_menu_must_be_menu(self):
        with pytest.raises(TypeError):
            CartItem(
                menu="아메리카노",
                quantity=Quantity(2),
                selected_options=[],
            )

    def test_quantity_must_be_quantity(self):
        with pytest.raises(TypeError):
            CartItem(
                menu=make_menu(),
                quantity=2,
                selected_options=[],
            )

    def test_selected_options_must_be_list(self):
        with pytest.raises(TypeError):
            CartItem(
                menu=make_menu(),
                quantity=Quantity(2),
                selected_options=(),
            )

    def test_selected_options_must_contain_option(self):
        with pytest.raises(TypeError):
            CartItem(
                menu=make_menu,
                quantity=Quantity(2),
                selected_options=[make_option(), "ice"],
            )

    def test_cart_item_total_price(self):
        menu = make_menu(price=3000)
        shot = make_option(price=500)
        syrup = make_option(price=300)

        cart_item = CartItem(
            menu=menu,
            quantity=Quantity(2),
            selected_options=[shot, syrup],
        )    

        assert cart_item.total_price() == Money(7600)