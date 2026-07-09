from src.domain.cart import Cart
from src.domain.cart_item import CartItem
from src.domain.inventory import Inventory
from src.domain.menu import Menu
from src.domain.option import Option
from src.domain.order import Order
from src.domain.payment import Payment
from src.domain.quantity import Quantity
from src.domain.exceptions import OutOfStockError


class OrderService:
    def __init__(self, payment: Payment, inventory: Inventory):
        self.payment = payment
        self.inventory = inventory

    def add_to_cart(
        self,
        cart: Cart,
        menu: Menu,
        quantity: Quantity,
        selected_options: list[Option],
    ) -> None:
        menu.validate_selected_options(selected_options)

        item = CartItem(menu=menu, quantity=quantity, selected_options=selected_options)
        cart.add_item(item)

    def checkout(self, cart: Cart) -> Order:
        order = Order.from_cart(cart)
        requirements = [(item.menu.recipe, item.quantity) for item in order.items]
        requirements += [
            (option.recipe, item.quantity)
            for item in order.items
            for option in item.selected_options
        ]

        if not self.inventory.can_consume_all(requirements):
            cart.clear()
            raise OutOfStockError()

        try:
            self.payment.pay(order)
        except Exception:
            cart.clear()
            raise

        self.inventory.consume_all(requirements)
        cart.clear()

        return order