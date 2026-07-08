from src.domain.exceptions import OutOfStockError
from src.domain.payment import Payment
from src.domain.inventory import Inventory
from src.domain.order import Order
from src.domain.cart import Cart
from src.domain.exceptions import InsufficientBalanceError
from src.domain.quantity import Quantity
from src.domain.menu import Menu
from src.domain.option import Option
from src.domain.cart_item import CartItem

class OrderService:
    def __init__(
            self,
            payment: Payment,
            inventory: Inventory,
    ):
        self.payment = payment
        self.inventory = inventory

    def checkout(self, cart: Cart) -> Order:
        order = Order.from_cart(cart)
        requirements = [(item.menu.recipe, item.quantity) for item in order.items]

        if not self.inventory.can_consume_all(requirements):
            cart.clear()
            raise OutOfStockError()

        try:
            self.payment.pay(order)
        except InsufficientBalanceError:
            cart.clear()
            raise

        self.inventory.consume_all(requirements)
        cart.clear()

        return order
    
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
    
        