from src.domain.inventory import Inventory
from src.infrastructure.db import Database
from src.infrastructure.repositories.postgres_inventory_repository import (
    PostgresInventoryRepository,
)


class PostgresInventoryPersister:
    def __init__(self, database: Database) -> None:
        self._database = database

    def persist(self, inventory: Inventory) -> None:
        with self._database.transaction() as connection:
            PostgresInventoryRepository(connection).save(inventory)
        # `Database.transaction()`이 반환하는 커넥션은 with 블록을
        # 정상 종료하면 자동 commit, 예외 시 자동 rollback 한다 (psycopg 기본 동작).