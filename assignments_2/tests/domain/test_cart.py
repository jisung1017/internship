import pytest

from src.domain.cart import Cart
from src.domain.cart_item import CartItem
from src.domain.ingredient import Ingredient
from src.domain.menu import Menu
from src.domain.money import Money
from src.domain.option import Option
from src.domain.quantity import Quantity
from src.domain.recipe import Recipe
from src.domain.recipe_item import RecipeItem


def create_menu(name: str, price: int) -> Menu:
    recipe = Recipe(
        items=[
            RecipeItem(
                ingredient=Ingredient("원두"),
                quantity=Quantity(1),
            )
        ]
    )

    return Menu(
        name=name,
        price=Money(price),
        recipe=recipe,
        option_groups=[],
    )


def create_cart_item(
    name: str,
    price: int,
    quantity: int,
    selected_options: list[Option] | None = None,
) -> CartItem:
    return CartItem(
        menu=create_menu(name, price),
        quantity=Quantity(quantity),
        selected_options=selected_options or [],
    )


class TestCartCreation:

    def test_create_cart(self):
        cart = Cart()

        assert cart.items == []


class TestCartAddition:

    def test_add_cart_item(self):
        cart = Cart()
        item = create_cart_item(
            name="아메리카노",
            price=3000,
            quantity=1,
        )

        cart.add_item(item)

        assert cart.items == [item]

    def test_total_price(self):
        cart = Cart()

        americano = create_cart_item(
            name="아메리카노",
            price=3000,
            quantity=2,
        )

        latte = create_cart_item(
            name="카페라떼",
            price=4000,
            quantity=1,
        )

        cart.add_item(americano)
        cart.add_item(latte)

        assert cart.total_price() == Money(10000)


class TestCartValidation:

    def test_add_non_cart_item_raises_type_error(self):
        cart = Cart()

        with pytest.raises(TypeError):
            cart.add_item("americano")