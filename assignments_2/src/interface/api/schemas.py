from datetime import datetime
from pydantic import BaseModel, Field

from src.domain.cart import Cart
from src.domain.cart_item import CartItem
from src.domain.menu import Menu
from src.domain.option import Option
from src.domain.option_group import OptionGroup
from src.domain.order_record import OrderRecord


# ---------- Catalog / Menu ----------

class OptionSchema(BaseModel):
    name: str
    additional_price: int

    @classmethod
    def from_domain(cls, option: Option) -> "OptionSchema":
        return cls(
            name=option.name,
            additional_price=option.additional_price.amount,
        )


class OptionGroupSchema(BaseModel):
    name: str
    min_quantity: int
    max_quantity: int
    selection_mode: str
    options: list[OptionSchema]

    @classmethod
    def from_domain(cls, group: OptionGroup) -> "OptionGroupSchema":
        return cls(
            name=group.name,
            min_quantity=group.min_quantity.value,
            max_quantity=group.max_quantity.value,
            selection_mode=group.selection_mode,
            options=[OptionSchema.from_domain(opt) for opt in group.options],
        )


class MenuResponse(BaseModel):
    name: str
    price: int
    option_groups: list[OptionGroupSchema]

    @classmethod
    def from_domain(cls, menu: Menu) -> "MenuResponse":
        return cls(
            name=menu.name,
            price=menu.price.amount,
            option_groups=[
                OptionGroupSchema.from_domain(g) for g in menu.option_groups
            ],
        )


# ---------- Cart ----------

class AddCartItemRequest(BaseModel):
    menu_name: str
    quantity: int = Field(..., ge=1, le=10)
    selected_options: list[str] = Field(default_factory=list)


class CartItemResponse(BaseModel):
    menu_name: str
    quantity: int
    selected_options: list[str]
    line_total: int

    @classmethod
    def from_domain(cls, item: CartItem) -> "CartItemResponse":
        return cls(
            menu_name=item.menu.name,
            quantity=item.quantity.value,
            selected_options=[opt.name for opt in item.selected_options],
            line_total=item.total_price().amount,
        )


class CartResponse(BaseModel):
    items: list[CartItemResponse]
    total_price: int

    @classmethod
    def from_domain(cls, cart: Cart) -> "CartResponse":
        return cls(
            items=[CartItemResponse.from_domain(item) for item in cart.items],
            total_price=cart.total_price().amount,
        )


# ---------- Order / Checkout ----------

class CreateOrderRequest(BaseModel):
    payment_balance: int = Field(..., ge=0)


class OrderResponse(BaseModel):
    order_id: int | None = None
    total_price: int
    remaining_balance: int


# ---------- Admin ----------

class RestockRequest(BaseModel):
    ingredient_name: str
    quantity: int = Field(..., gt=0)


class InventoryItemResponse(BaseModel):
    ingredient_name: str
    quantity: int
    unit: str


class InventoryHistoryResponse(BaseModel):
    ingredient_name: str
    change: int
    reason: str
    timestamp: datetime


class OrderRecordResponse(BaseModel):
    id: int | None
    created_at: datetime
    total_price: int

    @classmethod
    def from_domain(cls, record: OrderRecord) -> "OrderRecordResponse":
        return cls(
            id=record.id,
            created_at=record.created_at,
            total_price=record.total_price.amount,
        )


class TodaySalesResponse(BaseModel):
    total_sales: int
    orders: list[OrderRecordResponse]