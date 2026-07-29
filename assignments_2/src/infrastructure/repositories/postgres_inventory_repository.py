from abc import ABC, abstractmethod

from psycopg import Connection

from src.domain.ingredient import Ingredient
from src.domain.inventory import Inventory
from src.domain.inventory_item import InventoryItem
from src.domain.quantity import Quantity


class InventoryRepository(ABC):
    @abstractmethod
    def load(self) -> Inventory:
        """현재 재고를 조회한다."""
        raise NotImplementedError

    @abstractmethod
    def load_for_update(self, ingredient_names: list[str]) -> Inventory:
        """주어진 재료들의 재고 행을 잠근 채로 최신 값을 조회한다.

        (SELECT ... FOR UPDATE. 같은 트랜잭션이 끝날 때까지 다른 트랜잭션의
        동일 행에 대한 FOR UPDATE 조회를 대기시킨다.)
        """
        raise NotImplementedError

    @abstractmethod
    def save(self, inventory: Inventory) -> None:
        """재고 상태를 저장한다."""
        raise NotImplementedError


class PostgresInventoryRepository(InventoryRepository):
    def __init__(
        self,
        connection: Connection,
    ) -> None:
        self._connection = connection

    def load(self) -> Inventory:
        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    i.name,
                    i.unit,
                    inv.quantity
                FROM inventory AS inv
                JOIN ingredient AS i
                    ON i.id = inv.ingredient_id
                ORDER BY i.id
                """
            )

            rows = cursor.fetchall()

        return Inventory(
            items=[
                InventoryItem(
                    ingredient=Ingredient(
                        name=row["name"],
                        unit=row["unit"],
                    ),
                    quantity=Quantity(
                        row["quantity"],
                    ),
                )
                for row in rows
            ]
        )

    def load_for_update(self, ingredient_names: list[str]) -> Inventory:
        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    i.name,
                    i.unit,
                    inv.quantity
                FROM inventory AS inv
                JOIN ingredient AS i
                    ON i.id = inv.ingredient_id
                WHERE i.name = ANY(%(names)s)
                ORDER BY i.id
                FOR UPDATE OF inv
                """,
                {
                    "names": ingredient_names,
                },
            )

            rows = cursor.fetchall()

        return Inventory(
            items=[
                InventoryItem(
                    ingredient=Ingredient(
                        name=row["name"],
                        unit=row["unit"],
                    ),
                    quantity=Quantity(
                        row["quantity"],
                    ),
                )
                for row in rows
            ]
        )

    def save(
        self,
        inventory: Inventory,
    ) -> None:
        with self._connection.cursor() as cursor:
            for item in inventory.items:
                cursor.execute(
                    """
                    UPDATE inventory
                    SET quantity = %(quantity)s
                    WHERE ingredient_id = (
                        SELECT id
                        FROM ingredient
                        WHERE name = %(name)s
                    )
                    """,
                    {
                        "name": item.ingredient.name,
                        "quantity": item.quantity.value,
                    },
                )

                if cursor.rowcount != 1:
                    raise RuntimeError(
                        f"재고를 찾을 수 없습니다: {item.ingredient.name!r}"
                    )