from src.domain.inventory import Inventory
from src.domain.order import Order
from src.infrastructure.db import Database
from src.infrastructure.repositories.postgres_inventory_repository import (
    PostgresInventoryRepository,
)
from src.infrastructure.repositories.postgres_order_repository import (
    PostgresOrderRepository,
)


class PostgresOrderPersister:
    def __init__(self, database: Database) -> None:
        self._database = database

    def persist(self, order: Order, inventory: Inventory) -> None:
        with self._database.transaction() as connection:
            PostgresOrderRepository(connection).save(order)
            PostgresInventoryRepository(connection).save(inventory)
        # 위 with 블록이 정상 종료되면 주문 저장 + 재고 저장이 함께 commit,
        # 둘 중 하나라도 예외가 나면 둘 다 rollback (원자성 보장).