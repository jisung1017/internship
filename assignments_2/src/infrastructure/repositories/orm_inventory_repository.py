from sqlalchemy.orm import Session, joinedload

from src.application.inventory_repository import InventoryRepository
from src.domain.ingredient import Ingredient
from src.domain.inventory import Inventory
from src.domain.inventory_item import InventoryItem
from src.domain.quantity import Quantity
from src.infrastructure.models import IngredientModel, InventoryItemModel


class OrmInventoryRepository(InventoryRepository):
    """SQLAlchemy ORM 기반 재고 레포지토리 구현체"""

    def __init__(self, session: Session):
        self._session = session

    def load(self) -> Inventory:
        models = (
            self._session.query(InventoryItemModel)
            .options(joinedload(InventoryItemModel.ingredient))
            .order_by(InventoryItemModel.ingredient_id)
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

    def load_for_update(self, ingredient_names: list[str]) -> Inventory:
        models = (
            self._session.query(InventoryItemModel)
            .join(InventoryItemModel.ingredient)
            .filter(IngredientModel.name.in_(ingredient_names))
            .with_for_update()
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

    def save(self, inventory: Inventory) -> None:
        for item in inventory.items:
            model = (
                self._session.query(InventoryItemModel)
                .join(InventoryItemModel.ingredient)
                .filter(IngredientModel.name == item.ingredient.name)
                .first()
            )
            if model:
                model.quantity = item.quantity.value
            else:
                ing_model = (
                    self._session.query(IngredientModel)
                    .filter(IngredientModel.name == item.ingredient.name)
                    .first()
                )
                if not ing_model:
                    ing_model = IngredientModel(
                        name=item.ingredient.name, unit=item.ingredient.unit
                    )
                    self._session.add(ing_model)
                    self._session.flush()
                inv_model = InventoryItemModel(
                    ingredient_id=ing_model.id,
                    quantity=item.quantity.value,
                )
                self._session.add(inv_model)