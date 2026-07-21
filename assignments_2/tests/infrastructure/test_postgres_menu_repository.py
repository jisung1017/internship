from src.domain.quantity import Quantity
from src.infrastructure.repositories.postgres_menu_repository import (
    PostgresMenuRepository,
)


def _insert_menu(connection, name: str, price: int) -> int:
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO menu (name, price) VALUES (%s, %s) RETURNING id",
            (name, price),
        )
        return cursor.fetchone()["id"]


def _insert_ingredient(connection, name: str) -> int:
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO ingredient (name) VALUES (%s) RETURNING id",
            (name,),
        )
        return cursor.fetchone()["id"]


def _insert_recipe_item(connection, menu_id: int, ingredient_id: int, quantity: int) -> None:
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO recipe_item (menu_id, ingredient_id, quantity) VALUES (%s, %s, %s)",
            (menu_id, ingredient_id, quantity),
        )


def _insert_option_group(
    connection,
    menu_id: int,
    name: str,
    min_select: int,
    max_select: int,
    selection_mode: str,
) -> int:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO option_group (menu_id, name, min_select, max_select, selection_mode)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
            """,
            (menu_id, name, min_select, max_select, selection_mode),
        )
        return cursor.fetchone()["id"]


def _insert_option_item(connection, group_id: int, name: str, price: int) -> int:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO option_item (option_group_id, name, additional_price)
            VALUES (%s, %s, %s)
            RETURNING id
            """,
            (group_id, name, price),
        )
        return cursor.fetchone()["id"]


def _insert_option_recipe_item(connection, option_id: int, ingredient_id: int, quantity: int) -> None:
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO option_recipe_item (option_id, ingredient_id, quantity) VALUES (%s, %s, %s)",
            (option_id, ingredient_id, quantity),
        )


class TestFindAll:
    def test_assembles_recipe(self, connection):
        menu_id = _insert_menu(connection, "테스트메뉴1", 1000)
        bean_id = _insert_ingredient(connection, "테스트원두1")
        _insert_recipe_item(connection, menu_id, bean_id, 18)

        menus = PostgresMenuRepository(connection).find_all()
        menu = next(m for m in menus if m.name == "테스트메뉴1")

        assert len(menu.recipe.items) == 1
        assert menu.recipe.items[0].ingredient.name == "테스트원두1"
        assert menu.recipe.items[0].quantity == Quantity(18)

    def test_assembles_option_groups_in_insertion_order(self, connection):
        menu_id = _insert_menu(connection, "테스트메뉴2", 2000)
        bean_id = _insert_ingredient(connection, "테스트원두2")

        group1_id = _insert_option_group(connection, menu_id, "온도", 1, 1, "choice")
        _insert_option_item(connection, group1_id, "HOT", 0)
        _insert_option_item(connection, group1_id, "ICE", 0)

        group2_id = _insert_option_group(connection, menu_id, "샷추가", 0, 4, "count")
        shot_option_id = _insert_option_item(connection, group2_id, "샷추가", 500)
        _insert_option_recipe_item(connection, shot_option_id, bean_id, 10)

        menus = PostgresMenuRepository(connection).find_all()
        menu = next(m for m in menus if m.name == "테스트메뉴2")

        # 그룹 순서: 삽입 순서(온도 -> 샷추가) 그대로 유지되어야 한다
        assert [group.name for group in menu.option_groups] == ["온도", "샷추가"]

        temperature_group = menu.option_groups[0]
        assert {option.name for option in temperature_group.options} == {"HOT", "ICE"}

        shot_group = menu.option_groups[1]
        assert len(shot_group.options) == 1

        shot_option = shot_group.options[0]
        assert shot_option.additional_price.amount == 500
        assert shot_option.recipe.items[0].ingredient.name == "테스트원두2"
        assert shot_option.recipe.items[0].quantity == Quantity(10)

    def test_option_group_with_no_options_returns_empty_list(self, connection):
        menu_id = _insert_menu(connection, "테스트메뉴3", 1500)
        _insert_option_group(connection, menu_id, "빈그룹", 0, 1, "choice")

        menus = PostgresMenuRepository(connection).find_all()
        menu = next(m for m in menus if m.name == "테스트메뉴3")

        assert menu.option_groups[0].options == []


class TestFindByName:
    def test_returns_none_when_not_found(self, connection):
        menu = PostgresMenuRepository(connection).find_by_name("존재안하는메뉴")

        assert menu is None

    def test_returns_menu_with_full_assembly(self, connection):
        menu_id = _insert_menu(connection, "테스트메뉴4", 3000)
        bean_id = _insert_ingredient(connection, "테스트원두4")
        _insert_recipe_item(connection, menu_id, bean_id, 18)

        menu = PostgresMenuRepository(connection).find_by_name("테스트메뉴4")

        assert menu is not None
        assert menu.price.amount == 3000
        assert menu.recipe.items[0].ingredient.name == "테스트원두4"