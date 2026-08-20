from sqlalchemy import text
from sqlalchemy.orm import Session, joinedload

from src.domain.inventory_history import InventoryHistory
from src.application.inventory_repository import InventoryRepository
from src.domain.ingredient import Ingredient
from src.domain.inventory import Inventory
from src.domain.inventory_item import InventoryItem
from src.domain.quantity import Quantity
from src.infrastructure.models import IngredientModel, InventoryItemModel, InventoryHistoryModel


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

        inventory = Inventory(items=items)
        inventory._saved_history_count = 0
        return inventory

    def load_for_update(self, ingredient_names: list[str]) -> Inventory:
        """
        PostgreSQL Advisory Lock을 이용한 동시성 제어
        1. 요청된 원재료들의 PK ID를 가져와 오름차순 정렬 (데드락 100% 방지)
        2. pg_advisory_xact_lock(1000, id)으로 트랜잭션 단위 락 획득 (네임스페이스 분리)
        3. 최신 재고 조회 후 반환
        """
        if not ingredient_names:
            return self.load()

        # 중복 재료 이름 제거
        unique_names = list(set(ingredient_names))

        # 1. 락을 잡을 원재료 ID 조회 및 오름차순 정렬 (Lock Ordering)
        ing_models = (
            self._session.query(IngredientModel.id)
            .filter(IngredientModel.name.in_(unique_names))
            .order_by(IngredientModel.id.asc())
            .all()
        )

        # 7.4: 락 대상 검증 (요청 수와 DB 조회 수가 다르면 예외 발생)
        if len(ing_models) != len(unique_names):
            raise ValueError("재고 목록에 존재하지 않는 원재료가 포함되어 있습니다.")

        # 7.3: PostgreSQL Advisory Lock 획득 (2-인자 형태 락 키 네임스페이스 분리)
        bind_engine = self._session.get_bind()
        is_sqlite = bind_engine and bind_engine.dialect.name == "sqlite"

        if not is_sqlite:
            for (ing_id,) in ing_models:
                self._session.execute(
                    text("SELECT pg_advisory_xact_lock(1000, :id)"),
                    {"id": ing_id}
                )

        # 3. 락을 획득한 상태에서 최신 재고 수량 조회
        models = (
            self._session.query(InventoryItemModel)
            .join(InventoryItemModel.ingredient)
            .filter(IngredientModel.name.in_(unique_names))
            .order_by(InventoryItemModel.ingredient_id.asc())
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

        inventory = Inventory(items=items)
        inventory._locked_ingredient_names = set(unique_names)
        inventory._saved_history_count = 0
        return inventory

    def save(self, inventory: Inventory) -> None:
        # 범위 검증: load_for_update로 락을 잡은 범위 밖의 재료가 들어오면 예외 발생
        locked_names = getattr(inventory, "_locked_ingredient_names", None)
        
        # 락 정보가 아예 없는 Inventory 객체(load()로 조회 등)는 저장 전면 거부
        if locked_names is None:
            raise ValueError(
                "락이 설정되지 않은 Inventory 객체는 저장할 수 없습니다. load_for_update()를 사용하세요."
            )

        for item in inventory.items:
            if locked_names is not None and item.ingredient.name not in locked_names:
                raise ValueError(
                    f"락 범위({locked_names})에 포함되지 않은 원재료('{item.ingredient.name}')는 저장할 수 없습니다."
                )

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
                )

        # 새로 추가된 재고 이력(InventoryHistory)만 DB에 INSERT
        new_histories = inventory.history[inventory._saved_history_count:]

        for h in new_histories:
            ing_model = (
                self._session.query(IngredientModel)
                .filter(IngredientModel.name == h.ingredient.name)
                .first()
            )
            if ing_model:
                hist_model = InventoryHistoryModel(
                    ingredient_id=ing_model.id,
                    change=h.change,
                    reason=h.reason,
                    created_at=h.timestamp,
                )
                self._session.add(hist_model)

        inventory._saved_history_count = len(inventory.history)


    def find_histories(
        self,
        ingredient_name: str | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[InventoryHistory]:
        query = (
            self._session.query(InventoryHistoryModel)
            .options(joinedload(InventoryHistoryModel.ingredient))
            .join(InventoryHistoryModel.ingredient)
            .order_by(InventoryHistoryModel.id.desc())
        )
        if ingredient_name:
            query = query.filter(IngredientModel.name == ingredient_name)
        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)

        models = query.all()
        # ORM Model -> Domain InventoryHistory 변환하여 반환
        return [
            InventoryHistory(
                id=m.id,
                ingredient=Ingredient(
                    name=m.ingredient.name, unit=m.ingredient.unit
                ),
                change=m.change,
                reason=m.reason,
                timestamp=m.created_at,
            )
            for m in models
        ]