from dataclasses import dataclass
from uuid import UUID
from src.application.unit_of_work import AbstractUnitOfWork
from src.domain.ingredient import Ingredient
from src.domain.inventory import Inventory
from src.domain.money import Money
from src.domain.order_record import OrderRecord
from src.domain.quantity import Quantity
from src.domain.order_status import OrderStatus


@dataclass
class KioskAdminService:
    """관리자 유스케이스 조율 애플리케이션 서비스"""

    uow: AbstractUnitOfWork

    def get_inventory(self) -> Inventory:
        with self.uow:
            return self.uow.inventories.load()

    def restock(self, ingredient_name: str, quantity: Quantity) -> None:
        with self.uow:
            inventory = self.uow.inventories.load()
            inventory.restock(Ingredient(ingredient_name), quantity)
            self.uow.inventories.save(inventory)
            self.uow.commit()

    def get_today_orders(self, status: OrderStatus | None = None) -> list[OrderRecord]:
        with self.uow:
            return self.uow.orders.find_today(status=status)

    def get_today_sales_total(self) -> Money:
        with self.uow:
            records = self.uow.orders.find_today()
            total = Money(0)
            for record in records:
                if record.status != OrderStatus.CANCEL:
                    total = total.add(record.total_price)
            return total

    def update_order_status(self, order_uuid: UUID, new_status: OrderStatus) -> OrderRecord:
        """주문 상태 변경 및 취소 시 재고 자동 복구 유스케이스"""
        with self.uow:
            order_record = self.uow.orders.find_by_uuid(order_uuid)
            if not order_record:
                raise ValueError("주문 내역을 찾을 수 없습니다.")

            if order_record.status == OrderStatus.CANCEL:
                raise ValueError("이미 취소된 주문은 상태를 변경할 수 없습니다.")

            if order_record.status == new_status:
                return order_record

            if new_status == OrderStatus.CANCEL:
                self._restore_inventory_for_order(order_record)

            self.uow.orders.update_status(order_uuid, new_status)
            self.uow.commit()

            return self.uow.orders.find_by_uuid(order_uuid)

    def _restore_inventory_for_order(self, record: OrderRecord) -> None:
        """ 취소된 주문 내역을 바탕으로 원재료 재고 복구"""
        inventory = self.uow.inventories.load()

        for item in record.items:
            menu = self.uow.menus.find_by_name(item.menu_name)
            if not menu:
                continue

            for recipe_item in menu.recipe.items:
                restore_qty = recipe_item.quantity.multiply(item.quantity)
                inventory.restock(recipe_item.ingredient, restore_qty, reason="CANCEL")

            for opt_item in item.selected_options:
                opt_domain = menu.find_option_by_name(opt_item.option_name)
                if opt_domain and opt_domain.recipe:
                    for opt_recipe_item in opt_domain.recipe.items:
                        restore_qty = opt_recipe_item.quantity.multiply(item.quantity)
                        inventory.restock(opt_recipe_item.ingredient, restore_qty, reason="CANCEL")

        self.uow.inventories.save(inventory)