from dataclasses import dataclass
from uuid import UUID

from src.application.unit_of_work import AbstractUnitOfWork
from src.domain.cart import Cart
from src.domain.exceptions import OutOfStockError
from src.domain.inventory import Inventory
from src.domain.order import Order
from src.domain.order_record import OrderRecord
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
                inventory if inventory is not None else self.uow.inventories.load()
            )

            # 1. 도메인 객체 생성 및 레시피 요구량 도메인 위임 추출
            order = Order.from_cart(cart)
            requirements = order.get_recipe_requirements()

            try:
                # 2. 재고 검증
                if not current_inventory.can_consume_all(requirements):
                    raise OutOfStockError()

                # 3. 결제 진행 (Payment.pay 는 Order 객체를 인자로 받음)
                payment.pay(order)

                # 4. 재고 차감
                current_inventory.consume_all(requirements)

                # 5. 영속화 및 트랜잭션 커밋
                self.uow.orders.save(order)
                self.uow.inventories.save(current_inventory)
                self.uow.commit()

                return order
            finally:
                # 성공 및 모든 예외 상황 발생 시 일관되게 장바구니 정리
                cart.clear()

    def get_order_by_uuid(self, order_uuid: UUID) -> OrderRecord | None:
        with self.uow:
            return self.uow.orders.find_by_uuid(order_uuid)