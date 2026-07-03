import pytest

from src.domain.money import Money
from src.domain.quantity import Quantity
from src.domain.menu import Menu
from src.domain.option_group import OptionGroup
from src.domain.recipe import Recipe
from src.domain.recipe_item import RecipeItem
from src.domain.ingredient import Ingredient
from src.domain.cart_item import CartItem

def test_create_cart_item():
    americano = Menu(
        name="아메리카노",
        price=Money(3000),
        recipe=recipe,
    )

    shot = Option(
        name="샷 추가",
        quantity=Quantity,
        selected_options=[shot],
    )

    cart_item = CartItem(
        menu=americano,
        quantity=Quantity(2),
        selected_options=[shot],    
    )

    assert cart_item.total_price() == Money(7000)

def test_menu_must_be_menu():

def test_quantity_must_be_quantity():

def test_selected_options_must_be_list():

def test_selected_options_must_contain_option():