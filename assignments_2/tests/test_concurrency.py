import concurrent.futures
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.infrastructure.db import DEFAULT_DATABASE_URL
from src.infrastructure.models import Base
from src.infrastructure.unit_of_work import SqlAlchemyUnitOfWork
from src.infrastructure.seeder import seed_initial_data_from_json
from src.application.order_application_service import OrderApplicationService
from src.domain.quantity import Quantity
from src.domain.ingredient import Ingredient
from src.domain.exceptions import OutOfStockError


def setup_test_db():
    db_url = DEFAULT_DATABASE_URL
    if db_url.startswith("postgresql://"):
        db_url = db_url.replace("postgresql://", "postgresql+psycopg://")
    engine = create_engine(db_url, pool_pre_ping=True)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    session_factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    with session_factory() as session:
        seed_initial_data_from_json(session)

    return session_factory


class OrderDTO:
    def __init__(self, menu_name: str, quantity: int):
        self.menu_name = menu_name
        self.quantity = quantity
        self.selected_options = []


def test_concurrent_order_stock_limit():
    session_factory = setup_test_db()

    uow_init = SqlAlchemyUnitOfWork(session_factory=session_factory)
    with uow_init:
        inventory = uow_init.inventories.load()
        ing_bean = Ingredient("원두")
        current_qty = inventory.get_quantity(ing_bean)
        inventory.consume_all([(
            uow_init.menus.find_by_name("아메리카노").recipe,
            Quantity((current_qty.value - 90) // 18)
        )])
        uow_init.inventories.save(inventory)
        uow_init.commit()

    concurrent_request = 10
    success_count = 0
    fail_count = 0

    def place_order_worker(worker_id: int):
        thread_uow = SqlAlchemyUnitOfWork(session_factory=session_factory)
        service = OrderApplicationService(uow=thread_uow)

        dto = OrderDTO(menu_name="아메리카노", quantity=1)
        try:
            service.place_order_from_dto(items_dto=[dto])
            return True, None
        except OutOfStockError as e:
            return False, e
        except Exception as e:
            return False, e

    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_request) as executor:
        futures = [
            executor.submit(place_order_worker, i)
            for i in range(concurrent_request)
        ]

        for future in concurrent.futures.as_completed(futures):
            is_success, exc = future.result()
            if is_success:
                success_count += 1
            else:
                fail_count += 1

    uow_final = SqlAlchemyUnitOfWork(session_factory=session_factory)
    with uow_final:
        final_inventory = uow_final.inventories.load()
        final_bean_qty = final_inventory.get_quantity(Ingredient("원두")).value

    print(f"\n[동시성 테스트 결과]")
    print(f"- 성공한 주문: {success_count}건")
    print(f"- 실패한(품절) 주문: {fail_count}건")
    print(f"- 최종 원두 재고: {final_bean_qty}g")

    assert success_count == 5, f"성공 건수는 5건이어야 하지만 {success_count}건입니다."
    assert fail_count == 5, f"실패 건수는 5건이어야 하지만 {fail_count}건입니다."
    assert final_bean_qty == 0, f"최종 재고는 0g이어야 하지만 {final_bean_qty}g입니다."