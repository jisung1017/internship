from sqlalchemy.orm import Session, joinedload

from src.domain.ingredient import Ingredient
from src.domain.inventory import Inventory
from src.domain.inventory_item import InventoryItem
from src.domain.quantity import Quantity
from src.infrastructure.models import InventoryItemModel


class OrmInventoryRepository:
    """SQLAlchemy ORM 기반 재고 레포지토리 구현체"""

    def __init__(self, session: Session):
        self._session = session

    def get_all(self) -> Inventory:
        models = (
            self._session.query(InventoryItemModel)
            .options(joinedload(InventoryItemModel.ingredient))
            .all()
        )

        items = [
            InventoryItem(
                ingredient=Ingredient(
                    name=model.ingredient.name, unit=model.ingredient.unit
                ),
                quantity=Quantity(model.quantity),
            )
            for model in models
        ]

        return Inventory(items=items)