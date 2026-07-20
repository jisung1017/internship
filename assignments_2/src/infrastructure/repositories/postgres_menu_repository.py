from psycopg import Connection

from src.domain.menu import Menu
from src.domain.money import Money
from src.domain.recipe import Recipe
from src.domain.repositories.menu_repository import MenuRepository


class PostgresMenuRepository(MenuRepository):
    def __init__(
        self,
        connection: Connection,
    ) -> None:
        self._connection = connection

    def find_all(self) -> list[Menu]:
        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    name,
                    price
                FROM menu
                ORDER BY id
                """
            )

            rows = cursor.fetchall()

        return [
            Menu(
                name=row["name"],
                price=Money(row["price"]),
                recipe=Recipe(),
                option_groups=[],
            )
            for row in rows
        ]

    def find_by_name(
        self,
        name: str,
    ) -> Menu | None:
        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id,
                    name,
                    price
                FROM menu
                WHERE name = %(name)s
                """,
                {
                    "name": name,
                },
            )

            row = cursor.fetchone()

        if row is None:
            return None

        return Menu(
            name=row["name"],
            price=Money(row["price"]),
            recipe=Recipe(),
            option_groups=[],
        )