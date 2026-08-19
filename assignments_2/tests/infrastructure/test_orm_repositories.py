from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.domain.ingredient import Ingredient
from src.domain.money import Money
from src.domain.quantity import Quantity
from src.infrastructure.models import (
    Base,
    IngredientModel,
    InventoryHistoryModel,
    InventoryItemModel,
    MenuModel,
)
from src.infrastructure.repositories.orm_inventory_repository import (
    OrmInventoryRepository,
)
from src.infrastructure.repositories.orm_menu_repository import (
    OrmMenuRepository,
)


def setup_in_memory_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def test_orm_menu_repository():
    session = setup_in_memory_db()

    menu_model = MenuModel(name="아메리카노", price=3000)
    session.add(menu_model)
    session.commit()

    repo = OrmMenuRepository(session)
    menus = repo.find_all()

    assert len(menus) == 1
    assert menus[0].name == "아메리카노"
    assert menus[0].price == Money(3000)


def test_orm_inventory_repository():
    session = setup_in_memory_db()

    ing_model = IngredientModel(name="원두", unit="g")
    inv_model = InventoryItemModel(ingredient=ing_model, quantity=500)
    session.add_all([ing_model, inv_model])
    session.commit()

    repo = OrmInventoryRepository(session)
    inventory = repo.load()

    # inventory.items 리스트에서 원두 항목 찾기
    item = next((i for i in inventory.items if i.ingredient == Ingredient("원두", "g")), None)
    assert item is not None
    assert item.quantity == Quantity(500)


def test_inventory_history_accumulation_across_transactions():
    """여러 트랜잭션에 걸쳐 입고 수행 시 재고 이력이 정상 누적되어야 함"""
    session = setup_in_memory_db()

    ing_model = IngredientModel(name="원두", unit="g")
    inv_model = InventoryItemModel(ingredient=ing_model, quantity=1000)
    session.add_all([ing_model, inv_model])
    session.commit()

    repo = OrmInventoryRepository(session)

    # Round 1: 100g 입고
    inv1 = repo.load_for_update(["원두"])
    inv1.restock(Ingredient("원두", "g"), Quantity(100))
    repo.save(inv1)
    session.commit()

    # Round 2: 200g 입고
    inv2 = repo.load_for_update(["원두"])
    inv2.restock(Ingredient("원두", "g"), Quantity(200))
    repo.save(inv2)
    session.commit()

    # DB 이력 개수가 2개인지 검증 (회귀 2 발생 시 1개로 고정됨)
    histories = session.query(InventoryHistoryModel).all()
    assert len(histories) == 2
    assert histories[0].change == 100
    assert histories[1].change == 200