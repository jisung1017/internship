from sqlalchemy.orm import sessionmaker
from src.domain.inventory import Inventory
from src.infrastructure.repositories.orm_inventory_repository import OrmInventoryRepository

class OrmInventoryPersister:
    """SQLAlchemy ORM 기반의 InventoryPersister 구현체"""
    def __init__(self, session_factory: sessionmaker) -> None:
        self._session_factory = session_factory

    def persist(self, inventory: Inventory) -> None:
        with self._session_factory() as session:
            repo = OrmInventoryRepository(session)
            repo.save(inventory)
            session.commit()