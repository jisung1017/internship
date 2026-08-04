from datetime import datetime, timezone
from sqlalchemy.orm import Session

from src.domain.order import Order
from src.infrastructure.models import OrderItemModel, OrderModel


class OrmOrderPersister:
    """SQLAlchemy ORM 기반 주문 저장소 구현체"""

    def __init__(self, session: Session):
        self._session = session

    def save(self, order: Order) -> None:
        # 1. Order 엔티티의 total_price() 메서드 및 Money.amount 속성 사용
        order_model = OrderModel(
            total_price=order.total_price().amount,
            created_at=datetime.now(timezone.utc),
        )

        # 2. 개별 CartItem 엔티티의 total_price() 메서드 및 Quantity.value 사용
        for item in order.items:
            order_item_model = OrderItemModel(
                menu_name=item.menu.name,
                quantity=item.quantity.value,
                line_total=item.total_price().amount,
            )
            order_model.items.append(order_item_model)

        self._session.add(order_model)