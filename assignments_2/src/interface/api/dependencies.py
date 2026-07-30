from typing import Annotated

from fastapi import Depends, Request

from src.application.cart_service import CartService
from src.application.kiosk_admin_service import KioskAdminService
from src.application.kiosk_loader import KioskLoaderService
from src.application.order_application_service import OrderApplicationService
from src.domain.cart import Cart
from src.domain.inventory import Inventory
from src.domain.payment import Payment
from src.domain.money import Money
from src.infrastructure.db import Database
from src.infrastructure.repositories.postgres_inventory_persister import (
    PostgresInventoryPersister,
)
from src.infrastructure.repositories.postgres_inventory_repository import (
    PostgresInventoryRepository,
)
from src.infrastructure.repositories.postgres_menu_repository import (
    PostgresMenuRepository,
)
from src.infrastructure.repositories.postgres_order_history_reader import (
    PostgresOrderHistoryReader,
)
from src.infrastructure.repositories.postgres_order_persister import (
    PostgresOrderPersister,
)

# 인메모리 싱글톤 객체 관리 (초기화용)
_db = Database()
_loader = KioskLoaderService(
    database=_db,
    menu_repository_factory=PostgresMenuRepository,
    inventory_repository_factory=PostgresInventoryRepository,
)
_state = _loader.load()

# 메모리 상태 유지를 위한 싱글톤 인스턴스 (서버 실행 동안 유지)
_cart_service = CartService()
_order_app_service = OrderApplicationService(
    order_persister=PostgresOrderPersister(_db)
)
_admin_service = KioskAdminService(
    inventory=_state.inventory,
    inventory_persister=PostgresInventoryPersister(_db),
    order_history_reader=PostgresOrderHistoryReader(_db),
)
_global_cart = Cart()


def get_kiosk_state():
    return _state


def get_cart_service():
    return _cart_service


def get_order_app_service():
    return _order_app_service


def get_admin_service():
    return _admin_service


def get_global_cart():
    return _global_cart