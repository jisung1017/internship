from dataclasses import dataclass

from src.application.order_persister import OrderPersister
from src.domain.cart import Cart
from src.domain.exceptions import OutOfStockError
from src.domain.inventory import Inventory
from src.domain.order import Order
from src.domain.payment import Payment


@dataclass
class OrderApplicationService:
    """주문 확정, 재고 확인, 결제, 차감 및 영속화를 조율하는 무상태 유스케이스 서비스입니다."""

    order_persister: OrderPersister | None = None

    def place_order(self, cart: Cart, payment: Payment, inventory: Inventory) -> Order:
        order = Order.from_cart(cart)

        requirements = [(item.menu.recipe, item.quantity) for item in order.items]
        requirements += [
            (option.recipe, item.quantity)
            for item in order.items
            for option in item.selected_options
        ]

        if not inventory.can_consume_all(requirements):
            cart.clear()
            raise OutOfStockError()

        try:
            payment.pay(order)
        except Exception:
            cart.clear()
            raise

        inventory.consume_all(requirements)
        cart.clear()

        if self.order_persister is not None:
            self.order_persister.persist(order, inventory)

        return order