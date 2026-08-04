from typing import Any, Callable
from sqlalchemy.orm import Session

from src.application.unit_of_work import AbstractUnitOfWork
from src.infrastructure.repositories.orm_inventory_repository import (
    OrmInventoryRepository,
)
from src.infrastructure.repositories.orm_menu_repository import (
    OrmMenuRepository,
)
from src.infrastructure.repositories.orm_order_persister import (
    OrmOrderPersister,
)


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    """SQLAlchemy ORM 기반 Unit of Work 구현체입니다."""

    def __init__(self, session_factory: Callable[[], Session]):
        self.session_factory = session_factory

    def __enter__(self) -> AbstractUnitOfWork:
        self.session: Session = self.session_factory()
        self.menus = OrmMenuRepository(self.session)
        self.inventories = OrmInventoryRepository(self.session)
        self.orders = OrmOrderPersister(self.session)
        return super().__enter__()

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        try:
            super().__exit__(exc_type, exc_val, exc_tb)
        finally:
            self.session.close()

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()