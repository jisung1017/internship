from dataclasses import dataclass

from src.application.inventory_persister import InventoryPersister
from src.application.order_history_reader import OrderHistoryReader
from src.application.order_service import OrderService
from src.domain.ingredient import Ingredient
from src.domain.inventory import Inventory
from src.domain.money import Money
from src.domain.order_record import OrderRecord
from src.domain.quantity import Quantity


@dataclass
class KioskAdminService:

    # ---------- 개발자 모드 ----------

    order_service: OrderService
    inventory_persister: InventoryPersister | None = None
    order_history_reader: OrderHistoryReader | None = None

    def get_inventory(self) -> Inventory:
        return self.order_service.inventory

    def restock(self, ingredient_name: str, quantity: Quantity) -> None:
        self.order_service.inventory.restock(Ingredient(ingredient_name), quantity)
        self._persist_inventory()

    def get_today_orders(self) -> list[OrderRecord]:
        if self.order_history_reader is None:
            return []

        return self.order_history_reader.find_today()

    def get_today_sales_total(self) -> Money:
        total = Money(0)

        for record in self.get_today_orders():
            total = total.add(record.total_price)

        return total

    def _persist_inventory(self) -> None:
        if self.inventory_persister is not None:
            self.inventory_persister.persist(self.order_service.inventory)