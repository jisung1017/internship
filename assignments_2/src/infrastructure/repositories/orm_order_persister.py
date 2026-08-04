from datetime import datetime, timezone
from sqlalchemy.orm import Session

from src.domain.order import Order
from src.infrastructure.models import OrderItemModel, OrderModel


class OrmOrderPersister:
    """SQLAlchemy ORM 기반 주문 저장소 구현체
    
    Domain Entity의 결합도를 낮추기 위해 total_price 계산 및 created_at 추출 시
    도메인 객체의 인터페이스 다형성을 안전하게 처리합니다.
    """

    def __init__(self, session: Session):
        self._session = session

    def save(self, order: Order) -> None:
        # 1. Order 전체 금액 계산 (total_price 메서드 / 속성 대응)
        if hasattr(order, "total_price"):
            total_price_val = (
                order.total_price()
                if callable(order.total_price)
                else order.total_price
            )
            total_price_amount = (
                total_price_val.amount
                if hasattr(total_price_val, "amount")
                else int(total_price_val)
            )
        else:
            total_price_amount = 0

        # 2. 생성 시각 (도메인에 없으면 UTC 현재 시각 적용)
        created_at = getattr(order, "created_at", None) or datetime.now(timezone.utc)

        order_model = OrderModel(
            total_price=total_price_amount,
            created_at=created_at,
        )

        # 3. 개별 주문 항목(CartItem / OrderItem) 영속화
        for item in order.items:
            # line_total 금액 계산 (total_price / calculate_total_price / menu.price * quantity 순 안전 탐색)
            if hasattr(item, "total_price"):
                line_val = (
                    item.total_price()
                    if callable(item.total_price)
                    else item.total_price
                )
            elif hasattr(item, "calculate_total_price"):
                line_val = (
                    item.calculate_total_price()
                    if callable(item.calculate_total_price)
                    else item.calculate_total_price
                )
            else:
                # 기본 연산 fallback (menu.price * quantity)
                menu_price = (
                    item.menu.price.amount
                    if hasattr(item.menu.price, "amount")
                    else int(item.menu.price)
                )
                line_val = menu_price * item.quantity.value

            line_total_amount = (
                line_val.amount if hasattr(line_val, "amount") else int(line_val)
            )

            order_item_model = OrderItemModel(
                menu_name=item.menu.name,
                quantity=item.quantity.value,
                line_total=line_total_amount,
            )
            order_model.items.append(order_item_model)

        self._session.add(order_model)