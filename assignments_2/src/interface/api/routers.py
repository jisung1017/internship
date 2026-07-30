from fastapi import APIRouter, Depends, HTTPException, status

from src.application.cart_service import CartService
from src.application.kiosk_admin_service import KioskAdminService
from src.application.order_application_service import OrderApplicationService
from src.domain.cart import Cart
from src.domain.exceptions import InsufficientBalanceError, OutOfStockError
from src.domain.money import Money
from src.domain.option import Option
from src.domain.payment import Payment
from src.domain.quantity import Quantity
from src.interface.api.dependencies import (
    get_admin_service,
    get_cart_service,
    get_global_cart,
    get_kiosk_state,
    get_order_app_service,
)
from src.interface.api.schemas import (
    AddCartItemRequest,
    CartResponse,
    CreateOrderRequest,
    InventoryItemResponse,
    MenuResponse,
    OrderRecordResponse,
    OrderResponse,
    RestockRequest,
    TodaySalesResponse,
)

router = APIRouter(prefix="/api/v1")


# ---------- 메뉴 카탈로그 ----------

@router.get("/menus", response_model=list[MenuResponse])
def get_menus(state=Depends(get_kiosk_state)):
    return [MenuResponse.from_domain(menu) for menu in state.menus]


# ---------- 장바구니 ----------

@router.get("/cart", response_model=CartResponse)
def get_cart(cart: Cart = Depends(get_global_cart)):
    return CartResponse.from_domain(cart)


@router.post("/cart/items", response_model=CartResponse)
def add_cart_item(
    request: AddCartItemRequest,
    state=Depends(get_kiosk_state),
    cart: Cart = Depends(get_global_cart),
    cart_service: CartService = Depends(get_cart_service),
):
    menu = next((m for m in state.menus if m.name == request.menu_name), None)
    if not menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="존재하지 않는 메뉴입니다.",
        )

    # 1. Menu 내의 모든 Option 도메인 객체 수집
    available_options = [
        opt
        for group in menu.option_groups
        for opt in group.options
    ]

    # 2. 요청으로 온 문자열 옵션 이름들을 Option 도메인 객체로 변환
    selected_options: list[Option] = []
    for opt_name in request.selected_options:
        matched_option = next(
            (opt for opt in available_options if opt.name == opt_name), None
        )
        if not matched_option:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"존재하지 않는 옵션입니다: {opt_name}",
            )
        selected_options.append(matched_option)

    # 3. CartService의 add_item 호출
    try:
        cart_service.add_item(
            cart=cart,
            menu=menu,
            quantity=Quantity(request.quantity),
            selected_options=selected_options,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return CartResponse.from_domain(cart)


@router.delete("/cart")
def clear_cart(
    cart: Cart = Depends(get_global_cart),
    cart_service: CartService = Depends(get_cart_service),
):
    cart_service.clear_cart(cart)
    return {"message": "장바구니가 비워졌습니다."}


# ---------- 주문 / 결제 ----------

@router.post("/orders", response_model=OrderResponse)
def create_order(
    request: CreateOrderRequest,
    cart: Cart = Depends(get_global_cart),
    state=Depends(get_kiosk_state),
    order_service: OrderApplicationService = Depends(get_order_app_service),
):
    if len(cart) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="장바구니가 비어있습니다.",
        )

    payment = Payment(balance=Money(request.payment_balance))

    try:
        order = order_service.place_order(
            cart=cart,
            payment=payment,
            inventory=state.inventory,
        )
    except OutOfStockError as e:
        cart.clear()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except InsufficientBalanceError as e:
        cart.clear()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return OrderResponse(
        order_id=order.id,
        total_price=order.total_price.amount,
        remaining_balance=payment.balance.amount,
    )


# ---------- 관리자 API ----------

@router.get("/admin/inventory", response_model=list[InventoryItemResponse])
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


@router.post("/admin/inventory/restock")
def restock_inventory(
    request: RestockRequest,
    admin_service: KioskAdminService = Depends(get_admin_service),
):
    try:
        admin_service.restock(request.ingredient_name, Quantity(request.quantity))
    except (OutOfStockError, ValueError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return {"message": f"{request.ingredient_name} {request.quantity}개 입고 완료"}


@router.get("/admin/sales/today", response_model=TodaySalesResponse)
def get_today_sales(admin_service: KioskAdminService = Depends(get_admin_service)):
    total = admin_service.get_today_sales_total()
    records = admin_service.get_today_orders()

    return TodaySalesResponse(
        total_sales=total.amount,
        orders=[OrderRecordResponse.from_domain(r) for r in records],
    )