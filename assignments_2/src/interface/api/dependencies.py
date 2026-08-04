import os

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.application.cart_service import CartService
from src.application.kiosk_admin_service import KioskAdminService
from src.application.kiosk_loader import KioskLoaderService
from src.application.order_application_service import OrderApplicationService
from src.application.unit_of_work import AbstractUnitOfWork
from src.domain.cart import Cart
from src.infrastructure.db import DEFAULT_DATABASE_URL, Database
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
from src.infrastructure.unit_of_work import SqlAlchemyUnitOfWork

_DATABASE_URL = os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)
if _DATABASE_URL.startswith("postgresql://"):
    _SQLALCHEMY_DATABASE_URL = _DATABASE_URL.replace(
        "postgresql://", "postgresql+psycopg://"
    )
else:
    _SQLALCHEMY_DATABASE_URL = _DATABASE_URL

_engine = create_engine(_SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)
_session_factory = sessionmaker(
    autocommit=False, autoflush=False, bind=_engine
)

_db = Database()
_loader = KioskLoaderService(
    database=_db,
    menu_repository_factory=PostgresMenuRepository,
    inventory_repository_factory=PostgresInventoryRepository,
)
_state = _loader.load()

_cart_service = CartService()
_admin_service = KioskAdminService(
    inventory=_state.inventory,
    inventory_persister=PostgresInventoryPersister(_db),
    order_history_reader=PostgresOrderHistoryReader(_db),
)
_global_cart = Cart()


def get_uow() -> AbstractUnitOfWork:
    return SqlAlchemyUnitOfWork(session_factory=_session_factory)


def get_kiosk_state():
    return _state


def get_cart_service():
    return _cart_service


def get_order_app_service(
    uow: AbstractUnitOfWork = Depends(get_uow),
) -> OrderApplicationService:
    return OrderApplicationService(uow=uow)


def get_admin_service():
    return _admin_service


def get_global_cart():
    return _global_cart