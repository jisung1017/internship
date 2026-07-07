import pytest

from src.domain.exceptions import InsufficientBalanceError
from src.domain.exceptions import OutOfStockError
from src.domain.payment import Payment
from src.domain.cart import Cart
from src.domain.cart_item import CartItem
from src.domain.ingredient import Ingredient
from src.domain.menu import Menu
from src.domain.money import Money
from src.domain.option import Option
from src.domain.order import Order
from src.domain.quantity import Quantity
from src.domain.recipe import Recipe
from src.domain.recipe_item import RecipeItem
from src.domain.inventory import Inventory
from src.domain.inventory_item import InventoryItem
from src.application.order_service import OrderService

def create_menu(
    name: str,
    price: int,
    recipe: Recipe | None = None,
) -> Menu:
    return Menu(
        name=name,
        price=Money(price),
        recipe=recipe or create_recipe(),
        option_groups=[],
    )


def create_cart(*items: CartItem) -> Cart:
    cart = Cart()

    for item in items:
        cart.add_item(item)

    return cart


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



def create_recipe() -> Recipe:
    return Recipe(
        items=[
            RecipeItem(
                ingredient=Ingredient("원두"),
                quantity=Quantity(18),
            )
        ]
    )


def create_inventory() -> Inventory:
    return Inventory(
        items=[
            InventoryItem(Ingredient("원두"), Quantity(170)),
            InventoryItem(Ingredient("물"), Quantity(2500)),
        ]
    )


class TestOrderServiceValidation:
    def test_checkout_raises_out_of_stock_error_and_clears_cart(self):
        payment = Payment(balance=Money(10000))
        inventory = Inventory(
            items=[
                InventoryItem(Ingredient("원두"), Quantity(20)),
        ]
        )
        cart = create_cart(americano)

        service = OrderService(payment, inventory)

        with pytest.raises(OutOfStockError):
            service.checkout(cart)

        assert len(cart) == 0

    def test_checkout_raises_insufficient_balance_and_clear_cart(self):
        payment = Payment(balance=Money(100))
        inventory = create_inventory()
        cart = create_cart(americano)

        service = OrderService(payment, inventory)

        with pytest.raises(InsufficientBalanceError):
            service.checkout(cart)   

        assert len(cart) == 0


class TestOrderServiceAtomicity:
    def test_checkout_does_not_charge_when_is_out_of_stock(self):
        payment = Payment(balance=Money(10000))
        inventory = Inventory(
            items=[
                InventoryItem(Ingredient("원두"), Quantity(20)),
        ]
        )
        cart = create_cart(americano)

        service = OrderService(payment, inventory)

        with pytest.raises(OutOfStockError):
            service.checkout(cart)

        assert payment.balance == Money(100)