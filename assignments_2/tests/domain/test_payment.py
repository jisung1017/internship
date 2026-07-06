import pytest

from src.domain.cart import Cart
from src.domain.cart_item import CartItem
from src.domain.ingredient import Ingredient
from src.domain.menu import Menu
from src.domain.money import Money
from src.domain.option import Option
from src.domain.order import Order
from src.domain.payment import Payment
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


@pytest.fixture
def order():
    cart = Cart()

    cart.add_item(
        create_cart_item(
            name="아메리카노",
            price=3000,
            quantity=2,
        )
    )

    cart.add_item(
        create_cart_item(
            name="카페라떼",
            price=4000,
            quantity=1,
        )
    )

    return Order.from_cart(cart)


@pytest.fixture
def exact_balance_order():
    cart = Cart()

    cart.add_item(
        create_cart_item(
            name="아메리카노",
            price=5000,
            quantity=2,
        )
    )

    return Order.from_cart(cart)


class TestPaymentCreation:

    def test_create_payment(self):
        payment = Payment(balance=Money(50000))

        assert payment.balance == Money(50000)


class TestPaymentBehavior:

    def test_pay_order(self, order):
        payment = Payment(balance=Money(50000))

        payment.pay(order)

        assert payment.balance == Money(40000)

    def test_pay_exact_balance(self, exact_balance_order):
        payment = Payment(balance=Money(10000))

        payment.pay(exact_balance_order)

        assert payment.balance == Money(0)


class TestPaymentValidation:

    def test_balance_must_be_money(self):
        with pytest.raises(TypeError):
            Payment(balance=50000)

    def test_negative_balance_raises_value_error(self):
        with pytest.raises(ValueError):
            Payment(balance=Money(-1))

    def test_pay_requires_order(self):
        payment = Payment(balance=Money(50000))

        with pytest.raises(TypeError):
            payment.pay("order")

    def test_pay_insufficient_balance_raises_value_error(self, order):
        payment = Payment(balance=Money(5000))

        with pytest.raises(ValueError):
            payment.pay(order)
            
    def test_pay_only_once(self, order):
        payment = Payment(balance=Money(50000))

        payment.pay(order)

        with pytest.raises(ValueError):
            payment.pay(order)