import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from src.domain.money import Money
from src.domain.order import Order
from src.domain.order_record import OrderRecord, OrderRecordItem
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
        generated_uuid = order.order_uuid or uuid.uuid4()

        order_model = OrderModel(
            order_uuid=generated_uuid,
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
        order.order_uuid = order_model.order_uuid

    def find_by_uuid(self, order_uuid: uuid.UUID) -> OrderRecord | None:
        order_model = (
            self._session.query(OrderModel)
            .filter(OrderModel.order_uuid == order_uuid)
            .first()
        )
        if not order_model:
            return None

        items = []
        for item_model in order_model.items:
            options_total = sum(opt.additional_price for opt in item_model.options)
            line_total = (item_model.menu_price + options_total) * item_model.quantity
            items.append(
                OrderRecordItem(
                    menu_name=item_model.menu_name,
                    quantity=item_model.quantity,
                    line_total=Money(line_total),
                )
            )

        return OrderRecord(
            id=order_model.id,
            created_at=order_model.created_at,
            total_price=Money(order_model.total_price),
            items=items,
        )