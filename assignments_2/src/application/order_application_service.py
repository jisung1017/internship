from dataclasses import dataclass, field
from uuid import UUID

from src.application.cart_service import CartService
from src.application.unit_of_work import AbstractUnitOfWork
from src.domain.cart import Cart
from src.domain.exceptions import OutOfStockError
from src.domain.menu import Menu
from src.domain.money import Money
from src.domain.order import Order
from src.domain.order_record import OrderRecord
from src.domain.payment import Payment


@dataclass
class OrderApplicationService:
    """주문 관련 유스케이스 조율 애플리케이션 서비스"""

    uow: AbstractUnitOfWork
    cart_service: CartService = field(default_factory=CartService)

    def get_all_menus(self) -> list[Menu]:
        """전체 메뉴 조회 유스케이스"""
        with self.uow:
            return self.uow.menus.find_all()

            
    def place_order_from_dto(
        self,
        items_dto: list,
        is_payment_approved: bool = True, 
    ) -> Order:
        """DTO 기반 주문 생성 및 원자적 결제/차감 유스케이스"""
        with self.uow:
            # 1. 메뉴 조회 및 장바구니 구성
            available_menus = self.uow.menus.find_all()
            cart = Cart()
            for item in items_dto:
                self.cart_service.add_item_by_names(
                    cart=cart,
                    available_menus=available_menus,
                    menu_name=item.menu_name,
                    quantity_val=item.quantity,
                    selected_option_names=item.selected_options,
                )

            # 2. 주문 생성
            order = Order.from_cart(cart)
            requirements = order.get_recipe_requirements()

            # 3. 재고 상태 확인
            current_inventory = self.uow.inventories.load()
            if not current_inventory.can_consume_all(requirements):
                raise OutOfStockError()

            # 4. 결제 승인 시도 (성공/실패 판단)
            payment = Payment(is_approved=is_payment_approved)
            payment.pay(order)

            # 5. 재고 차감 및 영속화
            current_inventory.consume_all(requirements)
            self.uow.orders.save(order)
            self.uow.inventories.save(current_inventory)
            self.uow.commit()

            return order

        
    def get_order_by_uuid(self, order_uuid: UUID) -> OrderRecord | None:
        """UUID 기반 단건 주문 조회"""
        with self.uow:
            return self.uow.orders.find_by_uuid(order_uuid)