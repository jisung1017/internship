from src.domain.order_record import OrderRecord
from src.infrastructure.db import Database
from src.infrastructure.repositories.postgres_order_repository import (
    PostgresOrderRepository,
)


class PostgresOrderHistoryReader:
    def __init__(self, database: Database) -> None:
        self._database = database

    def find_today(self) -> list[OrderRecord]:
        with self._database.transaction() as connection:
            return PostgresOrderRepository(connection).find_today()