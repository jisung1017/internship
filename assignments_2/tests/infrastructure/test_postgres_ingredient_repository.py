from src.domain.ingredient import Ingredient
from src.infrastructure.repositories.postgres_ingredient_repository import (
    PostgresIngredientRepository,
)


def _insert_ingredient(connection, name: str, unit: str = "") -> int:
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO ingredient (name, unit) VALUES (%s, %s) RETURNING id",
            (name, unit),
        )
        return cursor.fetchone()["id"]


class TestFindAll:
    def test_returns_all_ingredients(self, connection):
        _insert_ingredient(connection, "테스트원두", "g")
        _insert_ingredient(connection, "테스트물", "ml")

        ingredients = PostgresIngredientRepository(connection).find_all()

        names = {ingredient.name for ingredient in ingredients}
        assert "테스트원두" in names
        assert "테스트물" in names


class TestFindByName:
    def test_returns_ingredient_when_exists(self, connection):
        _insert_ingredient(connection, "테스트원두")

        ingredient = PostgresIngredientRepository(connection).find_by_name("테스트원두")

        assert ingredient == Ingredient("테스트원두")

    def test_returns_none_when_not_exists(self, connection):
        ingredient = PostgresIngredientRepository(connection).find_by_name("존재안하는재료")

        assert ingredient is None