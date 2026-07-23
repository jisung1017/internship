from abc import ABC, abstractmethod

from psycopg import Connection

from src.domain.ingredient import Ingredient
from src.domain.menu import Menu
from src.domain.money import Money
from src.domain.option import Option
from src.domain.option_group import OptionGroup
from src.domain.quantity import Quantity
from src.domain.recipe import Recipe
from src.domain.recipe_item import RecipeItem


class MenuRepository(ABC):
    @abstractmethod
    def find_all(self) -> list[Menu]:
        """전체 메뉴를 조회한다."""
        raise NotImplementedError

    @abstractmethod
    def find_by_name(self, name: str) -> Menu | None:
        """이름으로 메뉴를 조회한다."""
        raise NotImplementedError


class PostgresMenuRepository(MenuRepository):
    def __init__(
        self,
        connection: Connection,
    ) -> None:
        self._connection = connection


class PostgresMenuRepository(MenuRepository):
    def __init__(
        self,
        connection: Connection,
    ) -> None:
        self._connection = connection

    def find_all(self) -> list[Menu]:
        recipe_items = self._load_recipe_items()
        option_groups = self._load_option_groups()

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
            self._build_menu(row, recipe_items, option_groups)
            for row in rows
        ]

    def find_by_name(
        self,
        name: str,
    ) -> Menu | None:
        recipe_items = self._load_recipe_items()
        option_groups = self._load_option_groups()

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

        return self._build_menu(row, recipe_items, option_groups)

    def _build_menu(
        self,
        row,
        recipe_items: dict[int, list[RecipeItem]],
        option_groups: dict[int, list[OptionGroup]],
    ) -> Menu:
        menu_id = row["id"]

        return Menu(
            name=row["name"],
            price=Money(
                row["price"],
            ),
            recipe=Recipe(
                items=recipe_items.get(menu_id, []),
            ),
            option_groups=option_groups.get(menu_id, []),
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

    def _load_option_recipe_items(
        self,
    ) -> dict[int, list[RecipeItem]]:
        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    ori.option_id,
                    i.name,
                    ori.quantity
                FROM option_recipe_item AS ori
                JOIN ingredient AS i
                    ON i.id = ori.ingredient_id
                ORDER BY
                    ori.option_id,
                    i.id
                """
            )

            rows = cursor.fetchall()

        recipe_items: dict[int, list[RecipeItem]] = {}

        for row in rows:
            option_id = row["option_id"]

            recipe_items.setdefault(
                option_id,
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

    def _load_option_groups(
        self,
    ) -> dict[int, list[OptionGroup]]:
        option_recipe_items = self._load_option_recipe_items()

        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    og.id AS group_id,
                    og.menu_id,
                    og.name AS group_name,
                    og.min_select,
                    og.max_select,
                    og.selection_mode,
                    oi.id AS option_id,
                    oi.name AS option_name,
                    oi.additional_price
                FROM option_group AS og
                LEFT JOIN option_item AS oi
                    ON oi.option_group_id = og.id
                ORDER BY
                    og.menu_id,
                    og.id,
                    oi.id
                """
            )

            rows = cursor.fetchall()

        group_meta: dict[int, dict] = {}
        group_options: dict[int, list[Option]] = {}
        menu_group_ids: dict[int, list[int]] = {}

        for row in rows:
            group_id = row["group_id"]

            if group_id not in group_meta:
                group_meta[group_id] = row
                group_options[group_id] = []
                menu_group_ids.setdefault(row["menu_id"], []).append(group_id)

            if row["option_id"] is not None:
                group_options[group_id].append(
                    Option(
                        name=row["option_name"],
                        additional_price=Money(row["additional_price"]),
                        recipe=Recipe(
                            items=option_recipe_items.get(row["option_id"], []),
                        ),
                    )
                )

        return {
            menu_id: [
                OptionGroup(
                    name=group_meta[group_id]["group_name"],
                    min_quantity=Quantity(group_meta[group_id]["min_select"]),
                    max_quantity=Quantity(group_meta[group_id]["max_select"]),
                    options=group_options[group_id],
                    selection_mode=group_meta[group_id]["selection_mode"],
                )
                for group_id in group_ids
            ]
            for menu_id, group_ids in menu_group_ids.items()
        }