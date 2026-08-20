import concurrent.futures, os
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest

from src.domain.cart import Cart
from src.domain.cart_item import CartItem
from src.domain.payment import Payment
from src.infrastructure.db import DEFAULT_DATABASE_URL
from src.infrastructure.models import Base
from src.infrastructure.unit_of_work import SqlAlchemyUnitOfWork
from src.infrastructure.seeder import seed_initial_data_from_json
from src.application.order_application_service import OrderApplicationService
from src.application.kiosk_admin_service import KioskAdminService
from src.domain.quantity import Quantity
from src.domain.ingredient import Ingredient
from src.domain.exceptions import OutOfStockError
from src.domain.order_status import OrderStatus


def setup_test_db():
    # TEST_DATABASE_URL 또는 명시적 DATABASE_URL 확인
    db_url = os.environ.get("TEST_DATABASE_URL") or os.environ.get("DATABASE_URL")

    # 미설정이거나 기본 개발 DB(kiosk)와 동일하면 개발 데이터 보호를 위해 테스트 skip
    if not db_url or db_url == DEFAULT_DATABASE_URL:
        pytest.skip("개발 DB 보호: TEST_DATABASE_URL 환경변수가 설정된 경우에만 동시성 DB 테스트를 수행합니다.")

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
            print(log_message)  # 터미널에 메시지 출력!
            
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


# =====================================================================
#  동시성 리뷰 반영 추가 테스트 케이스
# =====================================================================

def test_concurrent_duplicate_cancel():
    """문제 2 검증: 동일 주문을 동시 취소 시 1회만 성공하고 재고도 1회만 복구되어야 함"""
    session_factory = setup_test_db()

    # 1. 초기 주문 생성 (아메리카노 1잔: 원두 18g 차감)
    uow_setup = SqlAlchemyUnitOfWork(session_factory=session_factory)
    with uow_setup:
        order_service = OrderApplicationService(uow=uow_setup)
        order = order_service.place_order_from_dto([OrderDTO("아메리카노", 1)])
        order_id = order.id
        
        inv_after_order = uow_setup.inventories.load()
        initial_bean_qty = inv_after_order.get_quantity(Ingredient("원두")).value

    # 2. 동일 order_id에 대해 5개 스레드가 동시에 취소 요청
    cancel_requests = 5
    success_count = 0
    fail_count = 0

    def cancel_worker():
        uow = SqlAlchemyUnitOfWork(session_factory=session_factory)
        admin_service = KioskAdminService(uow=uow)
        try:
            admin_service.update_order_status(order_id, OrderStatus.CANCEL)
            return True
        except ValueError:
            return False

    with concurrent.futures.ThreadPoolExecutor(max_workers=cancel_requests) as executor:
        futures = [executor.submit(cancel_worker) for _ in range(cancel_requests)]
        for future in concurrent.futures.as_completed(futures):
            if future.result():
                success_count += 1
            else:
                fail_count += 1

    # 3. 검증: 정확히 1번만 취소 성공하고, 원두 재고는 18g만 복구되어야 함
    uow_final = SqlAlchemyUnitOfWork(session_factory=session_factory)
    with uow_final:
        final_inv = uow_final.inventories.load()
        final_bean_qty = final_inv.get_quantity(Ingredient("원두")).value

    assert success_count == 1, f"취소 성공은 1건이어야 하나 {success_count}건입니다."
    assert fail_count == cancel_requests - 1
    assert final_bean_qty == initial_bean_qty + 18, f"원두 재고는 18g만 증가해야 하나 {final_bean_qty - initial_bean_qty}g 증가했습니다."


def test_concurrent_cancel_and_order_mixed():
    """문제 1 검증: 취소(복구)와 주문(차감)이 동시에 실행될 때 차감 유실이 없어야 함"""
    session_factory = setup_test_db()

    # 1. 미리 취소용 주문 5건 생성 (아메리카노 1잔씩)
    cancel_order_ids = []
    uow_setup = SqlAlchemyUnitOfWork(session_factory=session_factory)
    with uow_setup:
        order_service = OrderApplicationService(uow=uow_setup)
        for _ in range(5):
            o = order_service.place_order_from_dto([OrderDTO("아메리카노", 1)])
            cancel_order_ids.append(o.id)
            
        inv_start = uow_setup.inventories.load()
        start_bean = inv_start.get_quantity(Ingredient("원두")).value

    # 2. 동시 실행: 기존 주문 5건 취소 (+90g 복구) vs 신규 아메리카노 주문 5건 (-90g 차감)
    def cancel_worker(target_id: int):
        uow = SqlAlchemyUnitOfWork(session_factory=session_factory)
        admin_service = KioskAdminService(uow=uow)
        admin_service.update_order_status(target_id, OrderStatus.CANCEL)

    def order_worker():
        uow = SqlAlchemyUnitOfWork(session_factory=session_factory)
        service = OrderApplicationService(uow=uow)
        service.place_order_from_dto([OrderDTO("아메리카노", 1)])

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(cancel_worker, oid) for oid in cancel_order_ids] + \
                  [executor.submit(order_worker) for _ in range(5)]
        for future in concurrent.futures.as_completed(futures):
            future.result()

    # 3. 검증: +90g - 90g = 시작 재고와 최종 재고가 동일해야 함
    uow_final = SqlAlchemyUnitOfWork(session_factory=session_factory)
    with uow_final:
        final_inv = uow_final.inventories.load()
        final_bean = final_inv.get_quantity(Ingredient("원두")).value

    assert final_bean == start_bean, f"최종 원두 재고({final_bean}g)가 시작 재고({start_bean}g)와 다릅니다. (덮어쓰기 유실 발생)"


def test_concurrent_idempotent_order_requests():
    """ 동일한 idempotency_key로 동시 요청 시 500 에러 없이 모두 동일 주문 반환"""
    session_factory = setup_test_db()
    same_idempotency_key = uuid.uuid4()

    def idempotent_worker():
        uow = SqlAlchemyUnitOfWork(session_factory=session_factory)
        service = OrderApplicationService(uow=uow)
        cart = Cart()
        menu = service.get_all_menus()[0]
        cart.add_item(CartItem(menu=menu, quantity=Quantity(1)))
        payment = Payment(is_approved=True)

        return service.place_order(cart=cart, payment=payment, order_uuid=same_idempotency_key)

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(idempotent_worker) for _ in range(5)]
        results = [future.result() for future in concurrent.futures.as_completed(futures)]

    # 5개의 요청이 모두 500 예외 없이 동일한 order_uuid를 반환해야 함
    first_uuid = results[0].order_uuid
    assert all(r.order_uuid == first_uuid for r in results)