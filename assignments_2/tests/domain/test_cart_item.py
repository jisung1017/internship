import pytest

from src.domain.cart_item import CartItem
from src.domain.ingredient import Ingredient
from src.domain.menu import Menu
from src.domain.money import Money
from src.domain.option import Option
from src.domain.quantity import Quantity
from src.domain.recipe import Recipe
from src.domain.recipe_item import RecipeItem

def create_recipe():
    return Recipe(
        items=[
            RecipeItem(
                ingredient=Ingredient("원두"),
                quantity=Quantity(18),
            )
        ]
    )

def test_create_cart_item():
    shot = Option(
        name="샷 추가",
        additional_price=Money(500),
    )

    menu = Menu(
        name="아메리카노",
        price=Money(3000),
        recipe=create_recipe(),
    )

    cart_item = CartItem(
        menu=menu,
        quantity=Quantity(2),
        selected_options=[shot],
    )

    assert cart_item.menu == menu
    assert cart_item.quantity == Quantity(2)
    assert cart_item.selected_options == [shot]

def test_menu_must_be_menu():
    with pytest.raises(TypeError):
        CartItem(
            menu="아메리카노",
            quantity=Quantity(2),
            selected_options=[],
        )

def test_quantity_must_be_quantity():
    menu = Menu(
        name="아메리카노",
        price=Money(3000),
        recipe=create_recipe(),
    )

    with pytest.raises(TypeError):
        CartItem(
            menu=menu,
            quantity=2,
            selected_options=[],
        )

def test_selected_options_must_be_list():
    menu = Menu(
        name="아메리카노",
        price=Money(3000),
        recipe=create_recipe(),
    )

    with pytest.raises(TypeError):
        CartItem(
            menu=menu,
            quantity=Quantity(2),
            selected_options=(),
        )

def test_selected_options_must_contain_option():
    menu = Menu(
        name="아메리카노",
        price=Money(3000),
        recipe=create_recipe(),
    )

    shot = Option(
        name="샷 추가",
        additional_price=Money(500),
    )

    with pytest.raises(TypeError):
        CartItem(
            menu=menu,
            quantity=Quantity(2),
            selected_options=[shot, "ice"],
        )

def test_cart_item_total_price():
    shot = Option(
        name="샷 추가",
        additional_price=Money(500),
    )

    syrup = Option(
        name="헤이즐넛",
        additional_price=Money(300),
    )

    menu = Menu(
        name="아메리카노",
        price=Money(3000),
        recipe=create_recipe(),
    )

    cart_item = CartItem(
        menu=menu,
        quantity=Quantity(2),
        selected_options=[shot, syrup],
    )    

    assert cart_item.total_price() == Money(7600)