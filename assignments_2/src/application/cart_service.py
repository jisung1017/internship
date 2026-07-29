from src.domain.cart import Cart
from src.domain.cart_item import CartItem
from src.domain.menu import Menu
from src.domain.option import Option
from src.domain.quantity import Quantity


class CartService:
    """장바구니 조작 유스케이스를 담당하는 무상태 서비스입니다."""

    def add_item(
        self,
        cart: Cart,
        menu: Menu,
        quantity: Quantity,
        selected_options: list[Option],
    ) -> None:
        menu.validate_selected_options(selected_options)

        item = CartItem(menu=menu, quantity=quantity, selected_options=selected_options)
        cart.add_item(item)

    def clear_cart(self, cart: Cart) -> None:
        cart.clear()