import os

import psycopg
import pytest
from psycopg.rows import dict_row

from src.domain.cart_item import CartItem
from src.domain.ingredient import Ingredient
from src.domain.inventory import Inventory
from src.domain.inventory_item import InventoryItem
from src.domain.menu import Menu
from src.domain.money import Money
from src.domain.order import Order
from src.domain.quantity import Quantity
from src.domain.recipe import Recipe
from src.infrastructure.db import DEFAULT_DATABASE_URL, Database
from src.infrastructure.repositories.postgres_order_persister import (
    PostgresOrderPersister,
)


def _dsn() -> str:
    return os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)


def _count_orders_with_menu(menu_name: str) -> int:
    with psycopg.connect(_dsn(), row_factory=dict_row) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT count(*) AS n
                FROM order_item
                WHERE menu_name = %s
                """,
                (menu_name,),
            )
            return cursor.fetchone()["n"]


class TestPostgresOrderPersister:
    def test_rolls_back_order_when_inventory_save_fails(self):
        menu = Menu(
            name="원자성테스트메뉴",
            price=Money(1000),
            recipe=Recipe(items=[]),
            option_groups=[],
        )
        order = Order(items=[CartItem(menu=menu, quantity=Quantity(1))])

        # 존재하지 않는 재료라서 InventoryRepository.save()가 RuntimeError를 낸다
        bad_inventory = Inventory(
            items=[InventoryItem(Ingredient("절대존재안하는재료"), Quantity(1))]
        )

        persister = PostgresOrderPersister(Database())

        with pytest.raises(RuntimeError):
            persister.persist(order, bad_inventory)

        assert _count_orders_with_menu("원자성테스트메뉴") == 0