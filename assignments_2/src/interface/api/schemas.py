from uuid import UUID
from pydantic import BaseModel, Field


# --- Menu Schemas ---
class OptionItemResponse(BaseModel):
    id: int = Field(..., description="옵션 아이템 PK ID")
    name: str
    additional_price: int


class OptionGroupResponse(BaseModel):
    name: str
    min_quantity: int
    max_quantity: int
    selection_mode: str
    options: list[OptionItemResponse]


class MenuResponse(BaseModel):
    name: str
    price: int
    option_groups: list[OptionGroupResponse]

    @classmethod
    def from_domain(cls, menu) -> "MenuResponse":
        return cls(
            name=menu.name,
            price=menu.price.amount,
            option_groups=[
                OptionGroupResponse(
                    name=group.name,
                    min_quantity=group.min_quantity.value,
                    max_quantity=group.max_quantity.value,
                    selection_mode=group.selection_mode,
                    options=[
                        OptionItemResponse(
                            id=opt.id or 0,
                            name=opt.name,
                            additional_price=opt.additional_price.amount,
                        )
                        for opt in group.options
                    ],
                )
                for group in menu.option_groups
            ],
        )


# --- Order Schemas ---
class OrderItemRequest(BaseModel):
    menu_name: str = Field(..., description="메뉴 이름", examples=["아메리카노"])
    quantity: int = Field(..., gt=0, description="주문 수량", examples=[1])
    selected_option_ids: list[int] = Field(
        default_factory=list,
        description="선택한 옵션 아이템 PK ID 목록",
        examples=[[1, 3]],
    )
    selected_options: list[str] = Field(
        default_factory=list,
        description="선택한 옵션 이름 목록 (하위 호환용)",
        examples=[["HOT", "샷 추가"]],
    )


class CreateOrderRequest(BaseModel):
    items: list[OrderItemRequest] = Field(
        ..., min_length=1, description="주문 항목 목록"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "items": [
                        {
                            "menu_name": "아메리카노",
                            "quantity": 1,
                            "selected_option_ids": [1, 3],
                        },
                        {
                            "menu_name": "카페라떼",
                            "quantity": 2,
                            "selected_option_ids": [2],
                        },
                    ]
                }
            ]
        }
    }


class OrderResponse(BaseModel):
    order_uuid: UUID = Field(..., description="생성된 주문 UUID")
    client_uuid: UUID = Field(..., description="요청한 클라이언트 UUID")
    total_price: int
    message: str = "주문이 성공적으로 접수되었습니다."


class OrderItemOptionResponse(BaseModel):
    option_name: str
    additional_price: int


class OrderRecordItemResponse(BaseModel):
    menu_name: str
    quantity: int
    line_total: int
    selected_options: list[OrderItemOptionResponse] = Field(default_factory=list)


class OrderDetailResponse(BaseModel):
    order_uuid: UUID
    created_at: str
    total_price: int
    items: list[OrderRecordItemResponse]

    @classmethod
    def from_domain(cls, record) -> "OrderDetailResponse":
        return cls(
            order_uuid=record.order_uuid,
            created_at=record.created_at.isoformat(),
            total_price=record.total_price.amount,
            items=[
                OrderRecordItemResponse(
                    menu_name=item.menu_name,
                    quantity=item.quantity,
                    line_total=item.line_total.amount,
                    selected_options=[
                        OrderItemOptionResponse(
                            option_name=opt.option_name,
                            additional_price=opt.additional_price.amount,
                        )
                        for opt in item.selected_options
                    ],
                )
                for item in record.items
            ],
        )


# --- Admin Schemas ---
class InventoryItemResponse(BaseModel):
    ingredient_name: str
    quantity: int
    unit: str


class RestockRequest(BaseModel):
    ingredient_name: str = Field(
        ..., description="재입고할 재고 이름", examples=["원두"]
    )
    quantity: int = Field(
        ..., gt=0, description="재입고 수량", examples=[100]
    )


class OrderRecordResponse(BaseModel):
    id: int
    created_at: str
    total_price: int
    items: list[OrderRecordItemResponse]

    @classmethod
    def from_domain(cls, record) -> "OrderRecordResponse":
        return cls(
            id=record.id,
            created_at=record.created_at.isoformat(),
            total_price=record.total_price.amount,
            items=[
                OrderRecordItemResponse(
                    menu_name=item.menu_name,
                    quantity=item.quantity,
                    line_total=item.line_total.amount,
                    selected_options=[
                        OrderItemOptionResponse(
                            option_name=opt.option_name,
                            additional_price=opt.additional_price.amount,
                        )
                        for opt in item.selected_options
                    ],
                )
                for item in record.items
            ],
        )


class TodaySalesResponse(BaseModel):
    total_sales: int
    orders: list[OrderRecordResponse]