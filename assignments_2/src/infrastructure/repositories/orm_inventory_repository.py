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
                # 이미 DB에 존재하는 재료의 수량만 갱신
                model.quantity = item.quantity.value
            else:
                # DB에 존재하지 않는 재료라면 자동 생성 대신 예외 발생
                raise ValueError(
                    f"DB 재고 목록에 존재하지 않는 원재료('{item.ingredient.name}')는 저장할 수 없습니다. "
                    f"먼저 원재료를 등록해 주세요."
                )