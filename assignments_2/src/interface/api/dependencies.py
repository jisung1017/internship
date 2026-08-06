import os

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.application.kiosk_loader import KioskState
from src.application.cart_service import CartService
from src.application.kiosk_admin_service import KioskAdminService
from src.application.order_application_service import OrderApplicationService
from src.application.unit_of_work import AbstractUnitOfWork
from src.infrastructure.repositories.orm_inventory_persister import OrmInventoryPersister
from src.infrastructure.db import DEFAULT_DATABASE_URL
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



def get_uow() -> AbstractUnitOfWork:
    return SqlAlchemyUnitOfWork(session_factory=_session_factory)


def get_kiosk_state(
    uow: AbstractUnitOfWork = Depends(get_uow),
) -> KioskState:
    with uow:
        menus = uow.menus.find_all()
        inventory = uow.inventories.load()
        return KioskState(menus=menus, inventory=inventory)


_cart_service = CartService()
def get_cart_service() -> CartService:
    return _cart_service


def get_order_app_service(
    uow: AbstractUnitOfWork = Depends(get_uow),
) -> OrderApplicationService:
    return OrderApplicationService(uow=uow)


def get_admin_service(
    uow: AbstractUnitOfWork = Depends(get_uow),
) -> KioskAdminService:
    with uow:
        inventory = uow.inventories.load()
        
    return KioskAdminService(
        inventory=inventory,
        inventory_persister=OrmInventoryPersister(_session_factory),
        order_history_reader=None,
    )