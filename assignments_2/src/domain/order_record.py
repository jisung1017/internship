from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID
from src.domain.money import Money
from src.domain.order_status import OrderStatus


@dataclass(frozen=True)
class OrderRecordItemOption:
    option_name: str
    additional_price: Money
    option_item_id: int | None = None 


@dataclass(frozen=True)
class OrderRecordItem:
    menu_name: str
    quantity: int
    line_total: Money
    selected_options: list[OrderRecordItemOption] = field(default_factory=list)
    menu_id: int | None = None 

@dataclass(frozen=True)
class OrderRecord:
    id: int
    order_uuid: UUID
    created_at: datetime
    total_price: Money
    items: list[OrderRecordItem]
    status: OrderStatus = OrderStatus.ORDERED