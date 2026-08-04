from datetime import datetime, timezone
from sqlalchemy.orm import Session

from src.domain.order import Order
from src.infrastructure.models import (
    OrderItemModel,
    OrderItemOptionModel,
    OrderModel,
)


class OrmOrderPersister:
    """SQLAlchemy ORM 기반 주문 저장소 구현체"""

    def __init__(self, session: Session):
        self._session = session

    def save(self, order: Order) -> None:
        order_model = OrderModel(
            total_price=order.total_price().amount,
            created_at=datetime.now(timezone.utc),
        )

        for item in order.items:
            order_item_model = OrderItemModel(
                menu_name=item.menu.name,
                menu_price=item.menu.price.amount,
                quantity=item.quantity.value,
            )
            for option in item.selected_options:
                option_model = OrderItemOptionModel(
                    option_name=option.name,
                    additional_price=option.additional_price.amount,
                )
                order_item_model.options.append(option_model)

            order_model.items.append(order_item_model)

        self._session.add(order_model)
        self._session.flush() 
        order.id = order_model.id 