import pytest
from src.domain.cart import Cart
from src.domain.cart_item import CartItem
from src.domain.ingredient import Ingredient
from src.domain.menu import Menu
from src.domain.money import Money
from src.domain.option_item import OptionItem
from src.domain.order import Order
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
    selected_options: list[OptionItem] | None = None,
) -> CartItem:
    return CartItem(
        menu=create_menu(name, price),
        quantity=Quantity(quantity),
        selected_options=selected_options or [],
    )


@pytest.fixture
def americano():
    return create_cart_item(
        name="아메리카노",
        price=3000,
        quantity=2,
    )


@pytest.fixture
def latte():
    return create_cart_item(
        name="카페라떼",
        price=4000,
        quantity=1,
    )


@pytest.fixture
def shot_option():
    return OptionItem(
        name="샷 추가",
        additional_price=Money(500),
    )


class TestOrderCreation:
    def test_create_order_requires_at_least_one_item(self):
        with pytest.raises(ValueError):
            Order(items=[])

    def test_create_order_from_cart(self, americano, latte):
        cart = Cart()
        cart.add_item(americano)
        cart.add_item(latte)
        order = Order.from_cart(cart)
        assert order.items == cart.items
        assert order.items is not cart.items

    def test_create_order_from_empty_cart_raises_value_error(self):
        cart = Cart()
        with pytest.raises(ValueError):
            Order.from_cart(cart)


class TestOrderBehavior:
    def test_total_price(self, americano, latte):
        order = Order(
            items=[americano, latte],
        )
        assert order.total_price() == Money(10000)

    def test_total_price_with_options(self, shot_option):
        americano = create_cart_item(
            name="아메리카노",
            price=3000,
            quantity=2,
            selected_options=[shot_option],
        )
        order = Order(
            items=[americano],
        )
        assert order.total_price() == Money(7000)


class TestOrderValidation:
    def test_items_must_be_list(self):
        with pytest.raises(TypeError):
            Order(items="americano")

    def test_items_must_contain_only_cart_items(self):
        with pytest.raises(TypeError):
            Order(items=["americano"])

    def test_from_cart_requires_cart(self):
        with pytest.raises(TypeError):
            Order.from_cart("cart")