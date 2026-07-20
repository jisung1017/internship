from src.domain.ingredient import Ingredient
from src.domain.repositories.ingredient_repository import IngredientRepository
from src.infrastructure.db import Database


class PostgresIngredientRepository(IngredientRepository):
    
    def __init__(self, database: Database) -> None:
        self._database = database

    def find_all(self) -> list[Ingredient]:
        with self._database.connect() as connection:
            with connection.cursor() as cursor:
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

    def find_by_name(self, name: str) -> Ingredient | None:
        with self._database.connect() as connection:
            with connection.cursor() as cursor:
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