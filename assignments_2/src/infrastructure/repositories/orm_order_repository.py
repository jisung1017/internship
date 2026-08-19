import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session, joinedload, selectinload
from src.application.order_repository import OrderRepository
from src.domain.money import Money
from src.domain.order import Order
from src.domain.order_status import OrderStatus
from src.domain.order_record import (
    OrderRecord,
    OrderRecordItem,
    OrderRecordItemOption,
)
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
            status=OrderStatus.ORDERED.value,
            created_at=datetime.now(timezone.utc),
        )
        for item in order.items:
            order_item_model = OrderItemModel(
                menu_id=item.menu.id,  
                menu_name=item.menu.name,
                menu_price=item.menu.price.amount,
                quantity=item.quantity.value,
            )
            for option in item.selected_options:
                option_model = OrderItemOptionModel(
                    option_item_id=option.id,  
                    option_name=option.name,
                    additional_price=option.additional_price.amount,
                )
                order_item_model.options.append(option_model)
            order_model.items.append(order_item_model)
        self._session.add(order_model)
        self._session.flush()
        order.id = order_model.id
        order.order_uuid = order_model.order_uuid

    def find_by_id(self, order_id: int) -> OrderRecord | None:
        order_model = (
            self._session.query(OrderModel)
            .filter(OrderModel.id == order_id)
            .options(joinedload(OrderModel.items).joinedload(OrderItemModel.options))
            .first()
        )
        if not order_model:
            return None
        return self._to_record(order_model)

    def find_by_id_for_update(self, order_id: int) -> OrderRecord | None:
        """비관적 락(FOR UPDATE)을 걸고 주문 레코드를 조회합니다."""
        bind_engine = self._session.get_bind()
        is_sqlite = bind_engine and bind_engine.dialect.name == "sqlite"

        query = (
            self._session.query(OrderModel)
            .filter(OrderModel.id == order_id)
            .options(
                selectinload(OrderModel.items).selectinload(OrderItemModel.options)
            )
        )
        if not is_sqlite:
            query = query.with_for_update(of=OrderModel)

        order_model = query.first()
        if not order_model:
            return None
        return self._to_record(order_model)

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

    def find_today(self, status: OrderStatus | None = None) -> list[OrderRecord]:
        """오늘 00:00:00 UTC 이후 생성된 주문 목록 조회"""
        today_start = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        query = self._session.query(OrderModel).filter(OrderModel.created_at >= today_start)
        if status is not None:
            status_val = status.value if isinstance(status, OrderStatus) else status
            query = query.filter(OrderModel.status == status_val)

        order_models = (
            query.options(
                joinedload(OrderModel.items).joinedload(OrderItemModel.options)
            )
            .order_by(OrderModel.id)
            .all()
        )
        return [self._to_record(model) for model in order_models]

    def update_status(self, order_uuid: uuid.UUID, new_status: OrderStatus) -> None:
        """주문 상태 업데이트"""
        order_model = (
            self._session.query(OrderModel)
            .filter(OrderModel.order_uuid == order_uuid)
            .first()
        )
        if not order_model:
            raise ValueError("존재하지 않는 주문입니다.")
        order_model.status = new_status.value

    def update_status_by_id(self, order_id: int, new_status: OrderStatus) -> None:
        order_model = (
            self._session.query(OrderModel)
            .filter(OrderModel.id == order_id)
            .first()
        )
        if not order_model:
            raise ValueError("존재하지 않는 주문입니다.")
        order_model.status = new_status.value

    def _to_record(self, order_model: OrderModel) -> OrderRecord:
        items = []
        for item_model in order_model.items:
            options_total = sum(
                opt.additional_price for opt in item_model.options
            )
            line_total = (
                item_model.menu_price + options_total
            ) * item_model.quantity

            selected_options = [
                OrderRecordItemOption(
                    option_item_id=opt.option_item_id,  
                    option_name=opt.option_name,
                    additional_price=Money(opt.additional_price),
                )
                for opt in item_model.options
            ]
            items.append(
                OrderRecordItem(
                    menu_id=item_model.menu_id,
                    menu_name=item_model.menu_name,
                    quantity=item_model.quantity,
                    line_total=Money(line_total),
                    selected_options=selected_options,
                )
            )
        return OrderRecord(
            id=order_model.id,
            order_uuid=order_model.order_uuid,
            created_at=order_model.created_at,
            total_price=Money(order_model.total_price),
            status=OrderStatus(order_model.status),
            items=items,
        )