from dataclasses import dataclass
from typing import Any, Callable
from psycopg import Connection

from src.application.inventory_repository import InventoryRepository
from src.application.menu_repository import MenuRepository
from src.domain.inventory import Inventory
from src.domain.menu import Menu


@dataclass(frozen=True)
class KioskState:
    menus: list[Menu]
    inventory: Inventory


class KioskLoaderService:
    """Application 계층에서 MenuRepository와 InventoryRepository를 조합하여
    키오스크 초기 상태(메뉴 목록 및 재고)를 로딩하는 유스케이스 서비스입니다.
    """

    def __init__(
        self,
        database: Any,
        menu_repository_factory: Callable[[Connection], MenuRepository],
        inventory_repository_factory: Callable[[Connection], InventoryRepository],
    ) -> None:
        self._database = database
        self._menu_repo_factory = menu_repository_factory
        self._inventory_repo_factory = inventory_repository_factory

    def load(self) -> KioskState:
        with self._database.transaction() as connection:
            menu_repo = self._menu_repo_factory(connection)
            inventory_repo = self._inventory_repo_factory(connection)

            menus = menu_repo.find_all()
            inventory = inventory_repo.load()

        return KioskState(menus=menus, inventory=inventory)