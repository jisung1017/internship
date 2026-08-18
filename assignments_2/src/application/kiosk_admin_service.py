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
            inventory = self.uow.inventories.load_for_update([ingredient_name])
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

    def update_order_status(self, order_id: int, new_status: OrderStatus) -> OrderRecord:
        """주문 상태 변경 및 취소 시 재고 자동 복구 유스케이스"""
        with self.uow:
            order_record = self.uow.orders.find_by_id(order_id)
            if not order_record:
                raise ValueError("주문 내역을 찾을 수 없습니다.")

            if order_record.status == OrderStatus.CANCEL:
                raise ValueError("이미 취소된 주문은 상태를 변경할 수 없습니다.")

            if order_record.status == new_status:
                return order_record

            if new_status == OrderStatus.CANCEL:
                self._restore_inventory_for_order(order_record)

            self.uow.orders.update_status_by_id(order_id, new_status)
            self.uow.commit()

            return self.uow.orders.find_by_id(order_id)

    def _restore_inventory_for_order(self, record: OrderRecord) -> None:
        all_menus_list = self.uow.menus.find_all()
        menus_by_id = {menu.id: menu for menu in all_menus_list if menu.id is not None}
        menus_by_name = {menu.name: menu for menu in all_menus_list}

        restore_map: dict[str, tuple[Ingredient, int]] = {}

        for item in record.items:
            menu = None
            if item.menu_id is not None:
                menu = menus_by_id.get(item.menu_id)
            if not menu:
                menu = menus_by_name.get(item.menu_name)

            if not menu:
                continue

            # 1. 메인 메뉴 레시피 복구 수량 계산
            for recipe_item in menu.recipe.items:
                ing = recipe_item.ingredient
                qty = recipe_item.quantity.value * item.quantity
                if ing.name in restore_map:
                    saved_ing, saved_qty = restore_map[ing.name]
                    restore_map[ing.name] = (saved_ing, saved_qty + qty)
                else:
                    restore_map[ing.name] = (ing, qty)

            # 2. 선택된 옵션 레시피 복구 수량 계산
            for opt_item in item.selected_options:
                opt_domain = None
                if opt_item.option_item_id is not None:
                    opt_domain = menu.find_option_item_by_id(opt_item.option_item_id)
                if not opt_domain:
                    opt_domain = menu.find_option_by_name(opt_item.option_name)

                if opt_domain and opt_domain.recipe:
                    for opt_recipe in opt_domain.recipe.items:
                        ing = opt_recipe.ingredient
                        qty = opt_recipe.quantity.value * item.quantity
                        if ing.name in restore_map:
                            saved_ing, saved_qty = restore_map[ing.name]
                            restore_map[ing.name] = (saved_ing, saved_qty + qty)
                        else:
                            restore_map[ing.name] = (ing, qty)

        # 3. 재고 반영
        inventory = self.uow.inventories.load()
        for _, (ingredient, total_qty) in restore_map.items():
            inventory.restock(
                ingredient, Quantity(total_qty), reason="CANCEL"
            )
        self.uow.inventories.save(inventory)