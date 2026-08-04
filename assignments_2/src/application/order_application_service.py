from dataclasses import dataclass

from src.application.unit_of_work import AbstractUnitOfWork
from src.domain.cart import Cart
from src.domain.exceptions import OutOfStockError
from src.domain.inventory import Inventory
from src.domain.order import Order
from src.domain.payment import Payment


@dataclass
class OrderApplicationService:
    """Unit of Work 패턴을 활용하여 주문, 재고 차감 및 결제 트랜잭션의 원자성을 보장하는 유스케이스 서비스입니다."""

    uow: AbstractUnitOfWork

    def place_order(
        self, cart: Cart, payment: Payment, inventory: Inventory | None = None
    ) -> Order:
        with self.uow:
            current_inventory = (
                inventory
                if inventory is not None
                else self.uow.inventories.load()
            )

            order = Order.from_cart(cart)

            requirements = [(item.menu.recipe, item.quantity) for item in order.items]
            requirements += [
                (option.recipe, item.quantity)
                for item in order.items
                for option in item.selected_options
            ]

            if not current_inventory.can_consume_all(requirements):
                cart.clear()
                raise OutOfStockError()

            try:
                payment.pay(order)
            except Exception:
                cart.clear()
                raise

            current_inventory.consume_all(requirements)
            cart.clear()

            self.uow.orders.save(order)
            self.uow.inventories.save(current_inventory)

            self.uow.commit()

            return order