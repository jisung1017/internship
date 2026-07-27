from src.application.kiosk_loader import KioskLoader
from src.infrastructure.db import Database
from src.infrastructure.repositories.postgres_inventory_repository import (
    PostgresInventoryRepository,
)
from src.infrastructure.repositories.postgres_menu_repository import (
    PostgresMenuRepository,
)


class PostgresKioskStateLoader:
    def __init__(self, database: Database) -> None:
        self._database = database

    def load(self) -> KioskLoader:
        with self._database.transaction() as connection:
            menus = PostgresMenuRepository(connection).find_all()
            inventory = PostgresInventoryRepository(connection).load()

        return KioskLoader(menus=menus, inventory=inventory)