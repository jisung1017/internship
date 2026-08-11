from fastapi import APIRouter, Depends, HTTPException, status

from src.application.kiosk_admin_service import KioskAdminService
from src.domain.exceptions import OutOfStockError
from src.domain.quantity import Quantity
from src.interface.api.dependencies import get_admin_service
from src.interface.api.schemas import (
    InventoryItemResponse,
    OrderRecordResponse,
    RestockRequest,
    TodaySalesResponse,
)

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])


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


@router.get("/sales/today", response_model=TodaySalesResponse)
def get_today_sales(admin_service: KioskAdminService = Depends(get_admin_service)):
    total = admin_service.get_today_sales_total()
    records = admin_service.get_today_orders()

    return TodaySalesResponse(
        total_sales=total.amount,
        orders=[OrderRecordResponse.from_domain(r) for r in records],
    )