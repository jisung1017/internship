from src.domain.cart_item import CartItem
from src.domain.menu import Menu
from src.domain.money import Money
from src.domain.option import Option
from src.domain.order import Order
from src.domain.quantity import Quantity
from src.domain.recipe import Recipe
from src.infrastructure.repositories.postgres_order_repository import (
    PostgresOrderRepository,
)


def _menu(name: str, price: int) -> Menu:
    return Menu(
        name=name,
        price=Money(price),
        recipe=Recipe(items=[]),
        option_groups=[],
    )


class TestSave:
    def test_saves_order_with_items_and_options(self, connection):
        menu = _menu("테스트메뉴", 3000)
        shot = Option(name="샷추가", additional_price=Money(500))
        cart_item = CartItem(menu=menu, quantity=Quantity(2), selected_options=[shot])
        order = Order(items=[cart_item])

        PostgresOrderRepository(connection).save(order)

        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT co.total_price
                FROM customer_order co
                JOIN order_item oi ON oi.order_id = co.id
                WHERE oi.menu_name = %s
                """,
                ("테스트메뉴",),
            )
            order_row = cursor.fetchone()
            # (3000 + 500) * 2
            assert order_row["total_price"] == 7000

            cursor.execute(
                "SELECT menu_name, menu_price, quantity FROM order_item WHERE menu_name = %s",
                ("테스트메뉴",),
            )
            item_row = cursor.fetchone()
            assert item_row["menu_name"] == "테스트메뉴"
            assert item_row["menu_price"] == 3000
            assert item_row["quantity"] == 2

            cursor.execute(
                """
                SELECT oio.option_name, oio.additional_price
                FROM order_item_option oio
                JOIN order_item oi ON oi.id = oio.order_item_id
                WHERE oi.menu_name = %s
                """,
                ("테스트메뉴",),
            )
            option_row = cursor.fetchone()
            assert option_row["option_name"] == "샷추가"
            assert option_row["additional_price"] == 500


class TestFindToday:
    def test_returns_today_order_with_correct_line_total(self, connection):
        menu = _menu("테스트메뉴2", 3000)
        shot = Option(name="샷추가", additional_price=Money(500))
        cart_item = CartItem(menu=menu, quantity=Quantity(1), selected_options=[shot])
        order = Order(items=[cart_item])

        repository = PostgresOrderRepository(connection)
        repository.save(order)

        records = repository.find_today()
        record = next(r for r in records if r.items[0].menu_name == "테스트메뉴2")

        assert record.total_price == Money(3500)
        assert record.items[0].line_total == Money(3500)  # 옵션 가격 포함

    def test_excludes_orders_from_other_days(self, connection):
        menu = _menu("테스트메뉴3", 1000)
        order = Order(items=[CartItem(menu=menu, quantity=Quantity(1))])

        repository = PostgresOrderRepository(connection)
        repository.save(order)

        # 방금 저장한 주문의 created_at을 어제로 되돌린다
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE customer_order
                SET created_at = created_at - interval '1 day'
                WHERE id = (
                    SELECT co.id
                    FROM customer_order co
                    JOIN order_item oi ON oi.order_id = co.id
                    WHERE oi.menu_name = %s
                )
                """,
                ("테스트메뉴3",),
            )

        records = repository.find_today()
        names = {item.menu_name for record in records for item in record.items}
        assert "테스트메뉴3" not in names