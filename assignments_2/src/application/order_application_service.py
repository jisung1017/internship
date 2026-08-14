from dataclasses import dataclass, field
from uuid import UUID
from src.application.cart_service import CartService
from src.application.unit_of_work import AbstractUnitOfWork
from src.domain.cart import Cart
from src.domain.exceptions import OutOfStockError
from src.domain.inventory import Inventory
from src.domain.menu import Menu
from src.domain.order import Order
from src.domain.order_record import OrderRecord
from src.domain.payment import Payment
from src.domain.category import Category
from src.domain.menu_tag import MenuTag


@dataclass
class OrderApplicationService:
    """주문 관련 유스케이스 조율 애플리케이션 서비스"""

    uow: AbstractUnitOfWork
    cart_service: CartService = field(default_factory=CartService)

    def get_all_menus(self) -> list[Menu]:
        with self.uow:
            return self.uow.menus.find_all()

    def get_all_menus_with_availability(
        self, category: Category | None = None, tag: MenuTag | None = None
    ) -> list[tuple[Menu, bool]]:
        """메뉴 목록 조회 및 재고 기반 품절 여부 판단 (서버 필터링 지원)"""
        with self.uow:
            menus = self.uow.menus.find_all(category=category, tag=tag)
            inventory = self.uow.inventories.load()
            return [(menu, menu.is_available(inventory)) for menu in menus]

    def place_order(
        self, cart: Cart, payment: Payment, inventory: Inventory | None = None
    ) -> Order:
        """장바구니와 결제 객체를 받아 주문을 결제/차감/저장하는 유스케이스"""
        with self.uow:
            order = Order.from_cart(cart)
            requirements = order.get_recipe_requirements()

            ingredient_names = list(
                {
                    recipe_item.ingredient.name
                    for recipe, _ in requirements
                    for recipe_item in recipe.items
                }
            )

            current_inventory = (
                inventory
                if inventory is not None
                else self.uow.inventories.load_for_update(ingredient_names)
            )
            try:
                if not current_inventory.can_consume_all(requirements):
                    raise OutOfStockError()
                payment.pay(order)
                current_inventory.consume_all(requirements)
                self.uow.orders.save(order)
                self.uow.inventories.save(current_inventory)
                self.uow.commit()
                return order
            finally:
                cart.clear()

    def place_order_from_dto(
        self,
        items_dto: list,
        is_payment_approved: bool = True,
    ) -> Order:
        available_menus = self.get_all_menus()
        cart = Cart()
        for item in items_dto:
            if hasattr(item, "selected_option_ids") and item.selected_option_ids:
                self.cart_service.add_item_by_ids(
                    cart=cart,
                    available_menus=available_menus,
                    menu_name=item.menu_name,
                    quantity_val=item.quantity,
                    selected_option_ids=item.selected_option_ids,
                )
            else:
                self.cart_service.add_item_by_names(
                    cart=cart,
                    available_menus=available_menus,
                    menu_name=item.menu_name,
                    quantity_val=item.quantity,
                    selected_option_names=getattr(item, "selected_options", []),
                )
        payment = Payment(is_approved=is_payment_approved)
        return self.place_order(cart=cart, payment=payment)

    def get_order_by_uuid(self, order_uuid: UUID) -> OrderRecord | None:
        with self.uow:
            return self.uow.orders.find_by_uuid(order_uuid)