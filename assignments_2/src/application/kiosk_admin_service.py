from dataclasses import dataclass

from src.application.unit_of_work import AbstractUnitOfWork
from src.domain.ingredient import Ingredient
from src.domain.inventory import Inventory
from src.domain.money import Money
from src.domain.order_record import OrderRecord
from src.domain.quantity import Quantity


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

    def get_today_orders(self) -> list[OrderRecord]:
        with self.uow:
            return self.uow.orders.find_today()

    def get_today_sales_total(self) -> Money:
        with self.uow:
            records = self.uow.orders.find_today()
            total = Money(0)
            for record in records:
                total = total.add(record.total_price)
            return total