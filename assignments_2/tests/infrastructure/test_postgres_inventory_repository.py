import pytest

from src.domain.ingredient import Ingredient
from src.domain.inventory import Inventory
from src.domain.inventory_item import InventoryItem
from src.domain.quantity import Quantity
from src.infrastructure.repositories.postgres_inventory_repository import (
    PostgresInventoryRepository,
)


def _insert_ingredient_with_stock(
    connection,
    name: str,
    quantity: int,
    unit: str = "",
) -> int:
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO ingredient (name, unit) VALUES (%s, %s) RETURNING id",
            (name, unit),
        )
        ingredient_id = cursor.fetchone()["id"]

        cursor.execute(
            "INSERT INTO inventory (ingredient_id, quantity) VALUES (%s, %s)",
            (ingredient_id, quantity),
        )

    return ingredient_id


class TestLoad:
    def test_loads_ingredient_with_quantity_and_unit(self, connection):
        _insert_ingredient_with_stock(connection, "테스트재료", 500, unit="g")

        inventory = PostgresInventoryRepository(connection).load()

        item = next(i for i in inventory.items if i.ingredient.name == "테스트재료")
        assert item.quantity == Quantity(500)
        assert item.ingredient.unit == "g"


class TestLoadForUpdate:
    def test_returns_only_requested_ingredients(self, connection):
        _insert_ingredient_with_stock(connection, "테스트원두A", 500, unit="g")
        _insert_ingredient_with_stock(connection, "테스트원두B", 300, unit="g")

        inventory = PostgresInventoryRepository(connection).load_for_update(
            ["테스트원두A"]
        )

        names = {item.ingredient.name for item in inventory.items}
        assert names == {"테스트원두A"}

        item = inventory.items[0]
        assert item.quantity == Quantity(500)
        assert item.ingredient.unit == "g"

    def test_returns_empty_inventory_when_no_match(self, connection):
        inventory = PostgresInventoryRepository(connection).load_for_update(
            ["존재안하는재료"]
        )

        assert inventory.items == []


class TestSave:
    def test_updates_quantity_in_db(self, connection):
        _insert_ingredient_with_stock(connection, "테스트재료", 500)

        inventory = Inventory(
            items=[InventoryItem(Ingredient("테스트재료"), Quantity(120))]
        )
        PostgresInventoryRepository(connection).save(inventory)

        reloaded = PostgresInventoryRepository(connection).load()
        item = next(i for i in reloaded.items if i.ingredient.name == "테스트재료")
        assert item.quantity == Quantity(120)

    def test_raises_when_ingredient_not_found(self, connection):
        inventory = Inventory(
            items=[InventoryItem(Ingredient("존재안하는재료"), Quantity(10))]
        )

        with pytest.raises(RuntimeError):
            PostgresInventoryRepository(connection).save(inventory)