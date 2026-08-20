from fastapi import APIRouter, Depends, HTTPException, Query, status
from uuid import UUID
from src.application.kiosk_admin_service import KioskAdminService
from src.domain.exceptions import OutOfStockError
from src.domain.quantity import Quantity
from src.domain.order_status import OrderStatus
from src.interface.api.dependencies import get_admin_service
from src.interface.api.schemas import (
    InventoryHistoryResponse,
    InventoryItemResponse,
    OrderRecordResponse,
    RestockRequest,
    TodaySalesResponse,
    UpdateOrderStatusRequest
)

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])


@router.get("/orders", response_model=list[OrderRecordResponse])
def get_admin_order(
    status: OrderStatus | None = None,
    admin_service: KioskAdminService = Depends(get_admin_service),
):
    records = admin_service.get_today_orders(status=status)
    return [OrderRecordResponse.from_domain(record) for record in records]


@router.patch("/orders/{order_id}/status", response_model=OrderRecordResponse)
def update_order_status(
    order_id: int,
    request: UpdateOrderStatusRequest,
    admin_service: KioskAdminService = Depends(get_admin_service),
):
    try:
        updated_record = admin_service.update_order_status(order_id=order_id, new_status=request.status)
        return OrderRecordResponse.from_domain(updated_record)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/inventory", response_model=list[InventoryItemResponse])
def get_inventory(admin_service: KioskAdminService = Depends(get_admin_service)):
    inventory = admin_service.get_inventory()
    return [
        InventoryItemResponse(
            ingredient_name=item.ingredient.name,
            quantity=item.quantity.value,
            unit=item.ingredient.unit,
        )
        for item in inventory.items
    ]


@router.post("/inventory/restock")
def restock_inventory(
    request: RestockRequest,
    admin_service: KioskAdminService = Depends(get_admin_service),
):
    try:
        admin_service.restock(request.ingredient_name, Quantity(request.quantity))
    except (OutOfStockError, ValueError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return {"message": f"{request.ingredient_name} {request.quantity}개 입고 완료"}


@router.get("/inventory/history", response_model=list[InventoryHistoryResponse])
def get_inventory_history(
    ingredient_name: str | None = Query(None, description="특정 재료명 필터"),
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(50, ge=1, le=100, description="페이지 크기"),
    admin_service: KioskAdminService = Depends(get_admin_service),
):
    records = admin_service.get_inventory_history(
        ingredient_name=ingredient_name,
        page=page,
        size=size,
    )
    return [
        InventoryHistoryResponse(
            id=record.id,
            ingredient_name=record.ingredient.name,
            change=record.change,
            reason=record.reason,
            created_at=record.timestamp.isoformat(),
        )
        for record in records
    ]


@router.get("/sales/today", response_model=TodaySalesResponse)
def get_today_sales(admin_service: KioskAdminService = Depends(get_admin_service)):
    total = admin_service.get_today_sales_total()
    records = admin_service.get_today_orders()

    return TodaySalesResponse(
        total_sales=total.amount,
        orders=[OrderRecordResponse.from_domain(r) for r in records],
    )