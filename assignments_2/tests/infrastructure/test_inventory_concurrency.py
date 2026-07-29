import threading
import time
import os

import psycopg
import pytest
from psycopg.rows import dict_row
from src.infrastructure.db import DEFAULT_DATABASE_URL
from src.infrastructure.repositories.postgres_inventory_repository import (
    PostgresInventoryRepository,
)


def _connect() -> psycopg.Connection:
    dsn = os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)
    return psycopg.connect(dsn, row_factory=dict_row)


@pytest.fixture
def locked_ingredient_name():
    """
    다른 커넥션에서도 보여야 하는 데이터라 커밋한다.
    (conftest.py의 connection fixture는 항상 롤백하므로 여기선 안 씀)
    끝나면 직접 지워서 흔적을 남기지 않는다.
    """
    name = "동시성테스트원두"

    setup_connection = _connect()
    with setup_connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO ingredient (name, unit) VALUES (%s, %s) RETURNING id",
            (name, "g"),
        )
        ingredient_id = cursor.fetchone()["id"]
        cursor.execute(
            "INSERT INTO inventory (ingredient_id, quantity) VALUES (%s, %s)",
            (ingredient_id, 100),
        )
    setup_connection.commit()

    yield name

    with setup_connection.cursor() as cursor:
        cursor.execute(
            "DELETE FROM inventory WHERE ingredient_id = %s", (ingredient_id,)
        )
        cursor.execute("DELETE FROM ingredient WHERE id = %s", (ingredient_id,))
    setup_connection.commit()
    setup_connection.close()


class TestRowLocking:
    def test_second_transaction_blocks_until_first_commits(
        self, locked_ingredient_name
    ):
        """
        A가 잠근 뒤 0.5초 있다가 커밋한다. B는 그동안 같은 행을 잠그려
        시도하는데, 최소 그 시간만큼은 실제로 블로킹돼야 한다.

        (두 커넥션의 "완료 시점"을 서로 이벤트 순서로 비교하면, 서로 다른
        네트워크 왕복이라 순서가 100% 보장되지 않아 드물게 흔들릴 수 있다.
        그래서 B 쪽 소요 시간만 단일 스레드에서 측정한다.)
        """
        connection_a = _connect()
        connection_b = _connect()
        a_locked = threading.Event()

        def hold_lock_then_release() -> None:
            PostgresInventoryRepository(connection_a).load_for_update(
                [locked_ingredient_name]
            )
            a_locked.set()  # B에게 "이제 잠갔다"를 확실하게 알린다

            time.sleep(0.5)
            connection_a.commit()  # 여기서 락이 풀린다

        thread = threading.Thread(target=hold_lock_then_release)
        thread.start()

        assert a_locked.wait(timeout=5), "A가 제한 시간 안에 락을 잡지 못했다"

        try:
            started_at = time.monotonic()
            # A가 커밋하기 전까지 이 호출은 블로킹돼야 한다
            PostgresInventoryRepository(connection_b).load_for_update(
                [locked_ingredient_name]
            )
            blocked_seconds = time.monotonic() - started_at
            connection_b.commit()
        finally:
            thread.join()
            connection_a.close()
            connection_b.close()

        # A가 락을 들고 있던 0.5초 중 대부분(최소 0.4초)은 B가 실제로 대기했어야 한다
        assert blocked_seconds >= 0.4, (
            f"FOR UPDATE가 걸리지 않은 것으로 보인다 (대기 시간: {blocked_seconds:.3f}초)"
        )

    def test_quantity_seen_by_second_transaction_reflects_first_commit(
        self, locked_ingredient_name
    ):
        """
        두 번째 트랜잭션이 재고를 다시 읽었을 때, 첫 번째 트랜잭션이 커밋한
        '최신 값'을 봐야 한다 (오래된 값을 보고 재고 판단을 하면 안 됨).
        """
        connection_a = _connect()
        connection_b = _connect()

        try:
            PostgresInventoryRepository(connection_a).load_for_update(
                [locked_ingredient_name]
            )

            with connection_a.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE inventory
                    SET quantity = quantity - 1
                    WHERE ingredient_id = (
                        SELECT id FROM ingredient WHERE name = %s
                    )
                    """,
                    (locked_ingredient_name,),
                )
            connection_a.commit()

            inventory = PostgresInventoryRepository(connection_b).load_for_update(
                [locked_ingredient_name]
            )
            connection_b.commit()

            item = inventory.items[0]
            assert item.quantity.value == 99  # 100 - 1
        finally:
            connection_a.close()
            connection_b.close()