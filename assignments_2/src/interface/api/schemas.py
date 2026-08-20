from uuid import UUID
from pydantic import BaseModel, Field
from src.domain.order_status import OrderStatus

# --- Menu Schemas ---
class OptionItemResponse(BaseModel):
    id: int = Field(..., description="옵션 아이템 PK ID", examples=[1])
    name: str = Field(..., description="옵션 이름 (예: HOT, Large)", examples=["Large"])
    additional_price: int = Field(..., description="추가 금액", examples=[500])


class OptionGroupResponse(BaseModel):
    name: str = Field(..., description="옵션 그룹명 (예: 온도, 사이즈, 샷 추가)", examples=["사이즈"])
    default_option_name: str | None = Field(
        None, description="기본 선택 옵션 이름 (예: Regular, HOT)", examples=["Regular"]
    )
    min_quantity: int = Field(..., description="최소 선택 수량", examples=[1])
    max_quantity: int = Field(..., description="최대 선택 수량", examples=[1])
    selection_mode: str = Field(..., description="선택 모드 (choice/count)", examples=["choice"])
    options: list[OptionItemResponse]


class MenuResponse(BaseModel):
    id: int
    name: str
    price: int
    category: str
    tags: list[str]
    is_available: bool
    option_groups: list[OptionGroupResponse]

    @classmethod
    def from_domain(cls, menu, is_available:bool) -> "MenuResponse":
        return cls(
            id=menu.id or 0,
            name=menu.name,
            price=menu.price.amount,
            category=menu.category.value,
            tags=[tag.value for tag in menu.tags],
            is_available=is_available,
            option_groups=[
                OptionGroupResponse(
                    name=group.name,
                    default_option_name=group.default_option_name,
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
        description="선택한 옵션 아이템 PK ID 목록 (온도, 사이즈, 샷추가 등)",
        examples=[[1, 4, 6]],
    )
    selected_options: list[str] = Field(
        default_factory=list,
        description="선택한 옵션 이름 목록",
        examples=[["ICE", "Large", "샷 추가"]],
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
                            "selected_option_ids": [1, 4, 6],
                            "selected_options": ["HOT", "MEDIUM", "샷 추가"],
                        },
                        {
                            "menu_name": "카페라떼",
                            "quantity": 2,
                            "selected_option_ids": [2, 4],
                            "selected_options": ["ICE", "MEDIUM"],
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
    status: str
    items: list[OrderRecordItemResponse]

    @classmethod
    def from_domain(cls, record) -> "OrderDetailResponse":
        return cls(
            order_uuid=record.order_uuid,
            created_at=record.created_at.isoformat(),
            total_price=record.total_price.amount,
            status=record.status.value,
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


class InventoryHistoryResponse(BaseModel):
    id: int | None = Field(..., description="이력 PK ID")
    ingredient_name: str = Field(..., description="재료명")
    change: int = Field(..., description="수량 변동량 (+입고 / -차감)")
    reason: str = Field(..., description="변동 사유 (RESTOCK, CONSUME, CANCEL)")
    created_at: str = Field(..., description="생성 일시 (ISO 8601)")


class UpdateOrderStatusRequest(BaseModel):
    status: OrderStatus = Field(..., description="변경할 주문 상태 (COMPLETE, CANCEL)")


class OrderRecordResponse(BaseModel):
    id: int
    order_uuid: UUID
    created_at: str
    total_price: int
    status: str
    items: list[OrderRecordItemResponse]

    @classmethod
    def from_domain(cls, record) -> "OrderRecordResponse":
        return cls(
            id=record.id,
            order_uuid=record.order_uuid,
            created_at=record.created_at.isoformat(),
            total_price=record.total_price.amount,
            status=record.status.value,
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