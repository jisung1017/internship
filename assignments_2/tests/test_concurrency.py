import concurrent.futures
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.infrastructure.db import DEFAULT_DATABASE_URL
from src.infrastructure.models import Base
from src.infrastructure.unit_of_work import SqlAlchemyUnitOfWork
from src.infrastructure.seeder import seed_initial_data_from_json
from src.application.order_application_service import OrderApplicationService
from src.application.kiosk_admin_service import KioskAdminService
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
        self.selected_options = ["HOT", "SMALL"]  # 필수 옵션


def test_concurrent_order_stock_limit():
    session_factory = setup_test_db()

    # 1. 원두 재고만 정확히 90g(아메리카노 5잔 분량)으로 설정
    uow_init = SqlAlchemyUnitOfWork(session_factory=session_factory)
    with uow_init:
        inventory = uow_init.inventories.load()
        for item in inventory.items:
            if item.ingredient.name == "원두":
                item.quantity = Quantity(90)
                break
        uow_init.inventories.save(inventory)
        uow_init.commit()

    # 2. 10개의 동시 주문 요청 준비
    concurrent_requests = 10
    success_count = 0
    fail_count = 0

    def place_order_worker(worker_id: int):
        thread_uow = SqlAlchemyUnitOfWork(session_factory=session_factory)
        service = OrderApplicationService(uow=thread_uow)
        dto = OrderDTO(menu_name="아메리카노", quantity=1)

        try:
            # 💡 성공 시 생성된 주문 정보 반환
            order = service.place_order_from_dto(items_dto=[dto])
            return True, f"Worker {worker_id:2d} -> 🟢 주문 성공 (Order ID: {order.id})"
        except OutOfStockError:
            return False, f"Worker {worker_id:2d} -> 🔴 품절 실패"
        except Exception as e:
            return False, f"Worker {worker_id:2d} -> 💥 예외 발생: {e}"

    print("\n\n================ [ 동시성 처리 상세 로그 ] ================")

    # 3. ThreadPoolExecutor로 10개 쓰레드 동시에 실행 및 결과 즉시 출력
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
        futures = [
            executor.submit(place_order_worker, i)
            for i in range(concurrent_requests)
        ]

        for future in concurrent.futures.as_completed(futures):
            is_success, log_message = future.result()
            print(log_message)  # 👈 터미널에 메시지 출력!
            
            if is_success:
                success_count += 1
            else:
                fail_count += 1

    # 4. 검증 및 결과 집계
    uow_final = SqlAlchemyUnitOfWork(session_factory=session_factory)
    with uow_final:
        final_inventory = uow_final.inventories.load()
        final_bean_qty = final_inventory.get_quantity(Ingredient("원두")).value

    print("==========================================================")
    print(f"\n[최종 요약]")
    print(f"- 성공한 주문: {success_count}건")
    print(f"- 실패한(품절) 주문: {fail_count}건")
    print(f"- 최종 원두 재고: {final_bean_qty}g\n")

    assert success_count == 5, f"성공 건수는 5건이어야 하지만 {success_count}건입니다."
    assert fail_count == 5, f"실패 건수는 5건이어야 하지만 {fail_count}건입니다."
    assert final_bean_qty == 0, f"최종 재고는 0g이어야 하지만 {final_bean_qty}g입니다."


def test_concurrent_restock_and_order():
    """주문(차감)과 입고(보충)가 동시에 일어날 때 데이터 유실이 없는지 검증"""
    session_factory = setup_test_db()

    # 초기 원두 재고 100g 설정
    uow_init = SqlAlchemyUnitOfWork(session_factory=session_factory)
    with uow_init:
        inventory = uow_init.inventories.load()
        for item in inventory.items:
            if item.ingredient.name == "원두":
                item.quantity = Quantity(100)
                break
        uow_init.inventories.save(inventory)
        uow_init.commit()

    # 동시 실행: 주문 5건(원두 -90g) + 입고 5건(원두 +500g) = 예상 최종 재고: 100 - 90 + 500 = 510g
    def order_worker():
        uow = SqlAlchemyUnitOfWork(session_factory=session_factory)
        service = OrderApplicationService(uow=uow)
        service.place_order_from_dto(items_dto=[OrderDTO("아메리카노", 1)])

    def restock_worker():
        uow = SqlAlchemyUnitOfWork(session_factory=session_factory)
        admin_service = KioskAdminService(uow=uow)
        admin_service.restock("원두", Quantity(100))

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        # 주문 5개, 입고 5개 동시에 던짐
        futures = [executor.submit(order_worker) for _ in range(5)] + \
                  [executor.submit(restock_worker) for _ in range(5)]
        
        for future in concurrent.futures.as_completed(futures):
            future.result()

    # 검증: 100g - (18g * 5) + (100g * 5) = 510g 이 나와야 정상!
    uow_final = SqlAlchemyUnitOfWork(session_factory=session_factory)
    with uow_final:
        final_inv = uow_final.inventories.load()
        final_bean = final_inv.get_quantity(Ingredient("원두")).value

    print(f"\n[주문+입고 동시성 결과] 최종 원두 재고: {final_bean}g (기대값: 510g)")
    assert final_bean == 510, f"최종 재고는 510g이어야 하지만 {final_bean}g입니다."