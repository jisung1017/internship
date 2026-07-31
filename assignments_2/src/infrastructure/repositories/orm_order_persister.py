from sqlalchemy.orm import Session

from src.domain.order import Order
from src.infrastructure.models import OrderItemModel, OrderModel


class OrmOrderPersister:
    """SQLAlchemy ORM 기반 주문 저장소 구현체"""

    def __init__(self, session: Session):
        self._session = session

    def save(self, order: Order) -> None:
        order_model = OrderModel(
            total_price=order.total_price.amount,
            created_at=order.created_at,
        )

        for item in order.items:
            order_item_model = OrderItemModel(
                menu_name=item.menu.name,
                quantity=item.quantity.value,
                line_total=item.calculate_total_price().amount,
            )
            order_model.items.append(order_item_model)

        self._session.add(order_model)
        self._session.commit()