from dataclasses import dataclass

from src.application.order_persister import OrderPersister
from src.application.order_service import OrderService
from src.domain.cart import Cart
from src.domain.order import Order


@dataclass
class CheckoutService:
    order_service: OrderService
    order_persister: OrderPersister | None = None

    def checkout(self, cart: Cart) -> Order:
        order = self.order_service.checkout(cart)

        if self.order_persister is not None:
            # 주문 이력 저장 + 재고 저장을 하나의 트랜잭션으로 원자적으로 처리
            self.order_persister.persist(order, self.order_service.inventory)

        return order