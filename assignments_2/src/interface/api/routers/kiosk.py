from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Response, status

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
    OrderDetailResponse,
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
    try:
        # 1. HTTP 요청 당 일회성 Cart 객체 생성
        cart = Cart()
        for item in request.items:
            cart_service.add_item_by_names(
                cart=cart,
                available_menus=state.menus,
                menu_name=item.menu_name,
                quantity_val=item.quantity,
                selected_option_names=item.selected_options,
            )

        payment = Payment(balance=Money(request.payment_balance))

        # 2. 주문 실행 (inventory 생략 -> UoW가 DB 최신 재고 자동 조회)
        order = order_service.place_order(
            cart=cart,
            payment=payment,
        )

        # 3. RESTful Location 헤더 설정
        response.headers["Location"] = f"/api/v1/orders/{order.order_uuid}"

        return OrderResponse(
            order_uuid=order.order_uuid,
            client_uuid=x_kiosk_uuid,
            total_price=order.total_price().amount,
            remaining_balance=payment.balance.amount,
            message="주문이 성공적으로 완료되었습니다.",
        )
    except (OutOfStockError, InsufficientBalanceError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/orders/{order_uuid}", response_model=OrderDetailResponse)
def get_order(
    order_uuid: UUID,
    order_service: OrderApplicationService = Depends(get_order_app_service),
):
    order_record = order_service.get_order_by_uuid(order_uuid)
    if not order_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="주문 정보를 찾을 수 없습니다.",
        )

    return OrderDetailResponse.from_domain(order_uuid, order_record)