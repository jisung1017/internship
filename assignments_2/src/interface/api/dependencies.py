import os
from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.application.kiosk_admin_service import KioskAdminService
from src.application.order_application_service import OrderApplicationService
from src.application.unit_of_work import AbstractUnitOfWork
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


def get_order_app_service(
    uow: AbstractUnitOfWork = Depends(get_uow),
) -> OrderApplicationService:
    return OrderApplicationService(uow=uow)


def get_admin_service(
    uow: AbstractUnitOfWork = Depends(get_uow),
) -> KioskAdminService:
    return KioskAdminService(uow=uow)