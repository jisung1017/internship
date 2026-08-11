import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session, joinedload
from src.application.order_repository import OrderRepository
from src.domain.money import Money
from src.domain.order import Order
from src.domain.order_record import OrderRecord, OrderRecordItem
from src.infrastructure.models import (
    OrderItemModel,
    OrderItemOptionModel,
    OrderModel,
)


class OrmOrderRepository(OrderRepository):
    """SQLAlchemy ORM 기반 OrderRepository 구현체"""

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
            .options(
                joinedload(OrderModel.items).joinedload(OrderItemModel.options)
            )
            .first()
        )
        if not order_model:
            return None
        return self._to_record(order_model)

    def find_today(self) -> list[OrderRecord]:
        """오늘 00:00:00 UTC 이후 생성된 주문 목록 조회"""
        today_start = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        order_models = (
            self._session.query(OrderModel)
            .filter(OrderModel.created_at >= today_start)
            .options(
                joinedload(OrderModel.items).joinedload(OrderItemModel.options)
            )
            .order_by(OrderModel.id)
            .all()
        )
        return [self._to_record(model) for model in order_models]

    def _to_record(self, order_model: OrderModel) -> OrderRecord:
        items = []
        for item_model in order_model.items:
            options_total = sum(
                opt.additional_price for opt in item_model.options
            )
            line_total = (
                item_model.menu_price + options_total
            ) * item_model.quantity
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