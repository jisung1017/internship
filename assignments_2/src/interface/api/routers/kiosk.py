from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, Header, HTTPException, Response, status
from src.application.order_application_service import OrderApplicationService
from src.domain.exceptions import OutOfStockError, PaymentFailedError
from src.interface.api.dependencies import get_order_app_service
from src.interface.api.schemas import (
    CreateOrderRequest,
    MenuResponse,
    OrderDetailResponse,
    OrderResponse,
)

router = APIRouter(prefix="/api/v1", tags=["Kiosk"])


@router.get("/menus", response_model=list[MenuResponse])
def get_menus(order_service: OrderApplicationService = Depends(get_order_app_service)):
    menus = order_service.get_all_menus_with_availability()
    return [MenuResponse.from_domain(menu, is_available=is_available) for menu, is_available in menus]


@router.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    request: CreateOrderRequest,
    response: Response,
    x_kiosk_uuid: Annotated[UUID, Header(description="클라이언트 키오스크 UUID")],
    order_service: OrderApplicationService = Depends(get_order_app_service),
):
    try:
        # 애플리케이션 서비스에 주문 생성 처리 위임
        order = order_service.place_order_from_dto(
            items_dto=request.items,
        )
        response.headers["Location"] = f"/api/v1/orders/{order.order_uuid}"
        return OrderResponse(
            order_uuid=order.order_uuid,
            client_uuid=x_kiosk_uuid,
            total_price=order.total_price().amount,
            message="주문이 성공적으로 접수되었습니다.",
        )
    except (OutOfStockError, PaymentFailedError, ValueError) as e:
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
            detail="주문 내역을 찾을 수 없습니다.",
        )
    return OrderDetailResponse.from_domain(order_record)