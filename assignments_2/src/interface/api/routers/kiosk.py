from fastapi import APIRouter, Depends, HTTPException, status

from src.application.cart_service import CartService
from src.application.order_application_service import OrderApplicationService
from src.domain.cart import Cart
from src.domain.exceptions import InsufficientBalanceError, OutOfStockError
from src.domain.money import Money
from src.domain.payment import Payment
from src.interface.api.dependencies import (
    get_cart_service,
    get_global_cart,
    get_kiosk_state,
    get_order_app_service,
)
from src.interface.api.schemas import (
    AddCartItemRequest,
    CartResponse,
    CreateOrderRequest,
    MenuResponse,
    OrderResponse,
)

router = APIRouter(prefix="/api/v1", tags=["Kiosk"])


@router.get("/menus", response_model=list[MenuResponse])
def get_menus(state=Depends(get_kiosk_state)):
    return [MenuResponse.from_domain(menu) for menu in state.menus]


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
    try:
        cart_service.add_item_by_names(
            cart=cart,
            available_menus=state.menus,
            menu_name=request.menu_name,
            quantity_val=request.quantity,
            selected_option_names=request.selected_options,
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


@router.post("/orders", response_model=OrderResponse)
def create_order(
    request: CreateOrderRequest,
    cart: Cart = Depends(get_global_cart),
    state=Depends(get_kiosk_state),
    order_service: OrderApplicationService = Depends(get_order_app_service),
):
    payment = Payment(balance=Money(request.payment_balance))

    try:
        order = order_service.place_order(
            cart=cart,
            payment=payment,
            inventory=state.inventory,
        )
    except (OutOfStockError, InsufficientBalanceError, ValueError) as e:
        cart.clear()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return OrderResponse(
        order_id=order.id,
        total_price=order.total_price.amount,
        remaining_balance=payment.balance.amount,
    )