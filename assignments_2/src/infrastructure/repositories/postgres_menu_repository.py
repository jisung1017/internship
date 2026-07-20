from psycopg import Connection

from src.domain.ingredient import Ingredient
from src.domain.menu import Menu
from src.domain.money import Money
from src.domain.quantity import Quantity
from src.domain.recipe import Recipe
from src.domain.recipe_item import RecipeItem
from src.domain.repositories.menu_repository import MenuRepository


class PostgresMenuRepository(MenuRepository):
    def __init__(
        self,
        connection: Connection,
    ) -> None:
        self._connection = connection

    def find_all(self) -> list[Menu]:
        recipe_items = self._load_recipe_items()

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
                price=Money(
                    row["price"],
                ),
                recipe=Recipe(),
                option_groups=[],
            )
            for row in rows
        ]

    def find_by_name(
        self,
        name: str,
    ) -> Menu | None:
        recipe_items = self._load_recipe_items()

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
            price=Money(
                row["price"],
            ),
            recipe=Recipe(),
            option_groups=[],
        )

    def _load_recipe_items(
        self,
    ) -> dict[int, list[RecipeItem]]:
        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    ri.menu_id,
                    i.name,
                    ri.quantity
                FROM recipe_item AS ri
                JOIN ingredient AS i
                    ON i.id = ri.ingredient_id
                ORDER BY
                    ri.menu_id,
                    i.id
                """
            )

            rows = cursor.fetchall()

        recipe_items: dict[int, list[RecipeItem]] = {}

        for row in rows:
            menu_id = row["menu_id"]

            recipe_items.setdefault(
                menu_id,
                [],
            ).append(
                RecipeItem(
                    ingredient=Ingredient(
                        name=row["name"],
                    ),
                    quantity=Quantity(
                        row["quantity"],
                    ),
                )
            )

        return recipe_items