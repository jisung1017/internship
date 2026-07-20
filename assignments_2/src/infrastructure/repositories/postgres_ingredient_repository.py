from psycopg import Connection

from src.domain.ingredient import Ingredient
from src.domain.repositories.ingredient_repository import IngredientRepository


class PostgresIngredientRepository(IngredientRepository):
    def __init__(
        self,
        connection: Connection,
    ) -> None:
        self._connection = connection

    def find_all(self) -> list[Ingredient]:
        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    name
                FROM ingredient
                ORDER BY id
                """
            )

            rows = cursor.fetchall()

        return [
            Ingredient(
                name=row["name"],
            )
            for row in rows
        ]

    def find_by_name(
        self,
        name: str,
    ) -> Ingredient | None:
        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    name
                FROM ingredient
                WHERE name = %(name)s
                """,
                {
                    "name": name,
                },
            )

            row = cursor.fetchone()

        if row is None:
            return None

        return Ingredient(
            name=row["name"],
        )