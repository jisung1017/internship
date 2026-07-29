from psycopg import Connection

from src.application.order_repository import OrderRepository
from src.domain.money import Money
from src.domain.order import Order
from src.domain.order_record import OrderRecord, OrderRecordItem


class PostgresOrderRepository(OrderRepository):
    def __init__(
        self,
        connection: Connection,
    ) -> None:
        self._connection = connection

    def save(self, order: Order) -> None:
        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO customer_order (total_price)
                VALUES (%(total_price)s)
                RETURNING id
                """,
                {
                    "total_price": order.total_price().amount,
                },
            )
            order_id = cursor.fetchone()["id"]

            for item in order.items:
                cursor.execute(
                    """
                    INSERT INTO order_item (order_id, menu_name, menu_price, quantity)
                    VALUES (%(order_id)s, %(menu_name)s, %(menu_price)s, %(quantity)s)
                    RETURNING id
                    """,
                    {
                        "order_id": order_id,
                        "menu_name": item.menu.name,
                        "menu_price": item.menu.price.amount,
                        "quantity": item.quantity.value,
                    },
                )
                order_item_id = cursor.fetchone()["id"]

                for option in item.selected_options:
                    cursor.execute(
                        """
                        INSERT INTO order_item_option (order_item_id, option_name, additional_price)
                        VALUES (%(order_item_id)s, %(option_name)s, %(additional_price)s)
                        """,
                        {
                            "order_item_id": order_item_id,
                            "option_name": option.name,
                            "additional_price": option.additional_price.amount,
                        },
                    )

    def find_today(self) -> list[OrderRecord]:
        with self._connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, created_at, total_price
                FROM customer_order
                WHERE created_at >= date_trunc('day', now())
                ORDER BY id
                """
            )
            order_rows = cursor.fetchall()

            records: list[OrderRecord] = []

            for order_row in order_rows:
                cursor.execute(
                    """
                    SELECT
                        oi.menu_name,
                        oi.menu_price,
                        oi.quantity,
                        COALESCE(SUM(oio.additional_price), 0) AS options_total
                    FROM order_item AS oi
                    LEFT JOIN order_item_option AS oio
                        ON oio.order_item_id = oi.id
                    WHERE oi.order_id = %(order_id)s
                    GROUP BY oi.id, oi.menu_name, oi.menu_price, oi.quantity
                    ORDER BY oi.id
                    """,
                    {
                        "order_id": order_row["id"],
                    },
                )
                item_rows = cursor.fetchall()

                records.append(
                    OrderRecord(
                        id=order_row["id"],
                        created_at=order_row["created_at"],
                        total_price=Money(order_row["total_price"]),
                        items=[
                            OrderRecordItem(
                                menu_name=item_row["menu_name"],
                                quantity=item_row["quantity"],
                                line_total=Money(
                                    (item_row["menu_price"] + item_row["options_total"])
                                    * item_row["quantity"]
                                ),
                            )
                            for item_row in item_rows
                        ],
                    )
                )

        return records