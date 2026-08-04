from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Header, Response

from src.application.cart_service import CartService
from src.application.order_application_service import OrderApplicationService
from src.domain.cart import Cart
from src.domain.exceptions import InsufficientBalanceError, OutOfStockError
from src.domain.money import Money
from src.domain.payment import Payment
from src.interface.api.dependencies import (
    get_cart_service,
    get_kiosk_state,
    get_order_app_service,
)
from src.interface.api.schemas import (
    CreateOrderRequest,
    MenuResponse,
    OrderResponse,
)

router = APIRouter(prefix="/api/v1", tags=["Kiosk"])

@router.get("/menus", response_model=list[MenuResponse])
def get_menus(state=Depends(get_kiosk_state)):
    return [MenuResponse.from_domain(menu) for menu in state.menus]

@router.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    request: CreateOrderRequest,
    response: Response,
    x_kiosk_uuid: Annotated[UUID, Header(description="키오스크 단말기 고유 UUID")],
    state=Depends(get_kiosk_state),
    order_service: OrderApplicationService = Depends(get_order_app_service),
    cart_service: CartService = Depends(get_cart_service),
):
    # 요청 시점에 일회성 장바구니 생성 (Stateless)
    cart = Cart()
    try:
        for item in request.items:
            cart_service.add_item_by_names(
                cart=cart,
                available_menus=state.menus,
                menu_name=item.menu_name,
                quantity_val=item.quantity,
                selected_option_names=item.selected_options,
            )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    payment = Payment(balance=Money(request.payment_balance))

    try:
        order = order_service.place_order(
            cart=cart,
            payment=payment,
            inventory=state.inventory,
        )
    except (OutOfStockError, InsufficientBalanceError, ValueError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    # RESTful 규약: 생성된 자원의 위치를 Location 헤더로 전달
    response.headers["Location"] = f"/api/v1/orders/{order.id}"

    return OrderResponse(
        order_id=order.id,
        client_uuid=x_kiosk_uuid,
        total_price=order.total_price().amount,
        remaining_balance=payment.balance.amount,
        message="주문이 성공적으로 완료되었습니다."
    )