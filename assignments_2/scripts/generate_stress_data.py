"""
스트레스 테스트용 대량 시드 데이터 생성 스크립트.

기존 002_init.sql 데이터(원두/물/우유/컵/시럽, 아메리카노 등)와 이름이
겹치지 않도록 전부 접두사("재료_", "메뉴_")를 붙여서 만든다.
그래서 안전하게 기존 데이터 위에 추가로 얹을 수 있고, 정리할 때도
접두사로 골라서 지우면 된다 (스크립트 맨 아래 정리 SQL 참고).

사용법:
    DATABASE_URL=... uv run python scripts/generate_stress_data.py
    (DATABASE_URL 안 주면 src/infrastructure/db.py의 기본값 사용)
"""

import os
import random
import time

import psycopg
from psycopg.rows import dict_row

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://kiosk:kiosk@localhost:5432/kiosk",
)

N_INGREDIENTS = 200
N_MENUS = 150
UNITS = ["g", "ml", "개"]
SELECTION_MODES = ["choice", "count"]

random.seed(42)  # 재현 가능하게 고정


def main() -> None:
    started_at = time.monotonic()

    with psycopg.connect(DATABASE_URL, row_factory=dict_row) as connection:
        ingredient_ids = _insert_ingredients(connection)
        _insert_inventory(connection, ingredient_ids)
        menu_ids = _insert_menus(connection)
        _insert_recipes(connection, menu_ids, ingredient_ids)
        _insert_options(connection, menu_ids, ingredient_ids)
        # with 블록이 정상 종료되면 commit

    elapsed = time.monotonic() - started_at
    print(f"완료. {elapsed:.2f}초 걸림.")
    print(f"재료 {N_INGREDIENTS}개, 메뉴 {N_MENUS}개 생성.")


def _insert_ingredients(connection) -> list[int]:
    ids = []
    with connection.cursor() as cursor:
        for i in range(1, N_INGREDIENTS + 1):
            cursor.execute(
                "INSERT INTO ingredient (name, unit) VALUES (%s, %s) RETURNING id",
                (f"재료_{i:04d}", random.choice(UNITS)),
            )
            ids.append(cursor.fetchone()["id"])
    return ids


def _insert_inventory(connection, ingredient_ids: list[int]) -> None:
    with connection.cursor() as cursor:
        for ingredient_id in ingredient_ids:
            cursor.execute(
                "INSERT INTO inventory (ingredient_id, quantity) VALUES (%s, %s)",
                (ingredient_id, random.randint(100, 5000)),
            )


def _insert_menus(connection) -> list[int]:
    ids = []
    with connection.cursor() as cursor:
        for i in range(1, N_MENUS + 1):
            price = random.randint(20, 80) * 100  # 2000~8000원, 100원 단위
            cursor.execute(
                "INSERT INTO menu (name, price) VALUES (%s, %s) RETURNING id",
                (f"메뉴_{i:04d}", price),
            )
            ids.append(cursor.fetchone()["id"])
    return ids


def _insert_recipes(connection, menu_ids: list[int], ingredient_ids: list[int]) -> None:
    with connection.cursor() as cursor:
        for menu_id in menu_ids:
            picked = random.sample(ingredient_ids, k=random.randint(2, 6))
            for ingredient_id in picked:
                cursor.execute(
                    """
                    INSERT INTO recipe_item (menu_id, ingredient_id, quantity)
                    VALUES (%s, %s, %s)
                    """,
                    (menu_id, ingredient_id, random.randint(1, 50)),
                )


def _insert_options(connection, menu_ids: list[int], ingredient_ids: list[int]) -> None:
    with connection.cursor() as cursor:
        for menu_id in menu_ids:
            for group_index in range(random.randint(0, 3)):
                mode = random.choice(SELECTION_MODES)

                if mode == "choice":
                    cursor.execute(
                        """
                        INSERT INTO option_group
                            (menu_id, name, min_select, max_select, selection_mode)
                        VALUES (%s, %s, 1, 1, 'choice')
                        RETURNING id
                        """,
                        (menu_id, f"옵션그룹_{menu_id}_{group_index}"),
                    )
                    group_id = cursor.fetchone()["id"]

                    for option_index in range(random.randint(2, 4)):
                        cursor.execute(
                            """
                            INSERT INTO option_item
                                (option_group_id, name, additional_price)
                            VALUES (%s, %s, 0)
                            """,
                            (group_id, f"선택지_{option_index}"),
                        )
                else:
                    cursor.execute(
                        """
                        INSERT INTO option_group
                            (menu_id, name, min_select, max_select, selection_mode)
                        VALUES (%s, %s, 0, 4, 'count')
                        RETURNING id
                        """,
                        (menu_id, f"옵션그룹_{menu_id}_{group_index}"),
                    )
                    group_id = cursor.fetchone()["id"]

                    cursor.execute(
                        """
                        INSERT INTO option_item
                            (option_group_id, name, additional_price)
                        VALUES (%s, %s, %s)
                        RETURNING id
                        """,
                        (
                            group_id,
                            f"추가옵션_{menu_id}_{group_index}",
                            random.randint(1, 10) * 100,
                        ),
                    )
                    option_id = cursor.fetchone()["id"]

                    for ingredient_id in random.sample(
                        ingredient_ids, k=random.randint(1, 3)
                    ):
                        cursor.execute(
                            """
                            INSERT INTO option_recipe_item
                                (option_id, ingredient_id, quantity)
                            VALUES (%s, %s, %s)
                            """,
                            (option_id, ingredient_id, random.randint(1, 20)),
                        )


if __name__ == "__main__":
    main()

# ============================================================
# 정리(전부 삭제)하고 싶을 때:
#
# DELETE FROM ingredient WHERE name LIKE '재료\_%';
# DELETE FROM menu WHERE name LIKE '메뉴\_%';
# (FK가 ON DELETE CASCADE라 recipe_item/option_group/option_item/
#  option_recipe_item/inventory는 같이 지워진다)
# ============================================================