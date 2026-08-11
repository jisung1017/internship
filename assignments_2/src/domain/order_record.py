from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID
from src.domain.money import Money


@dataclass(frozen=True)
class OrderRecordItemOption:
    option_name: str
    additional_price: Money


@dataclass(frozen=True)
class OrderRecordItem:
    menu_name: str
    quantity: int
    line_total: Money
    selected_options: list[OrderRecordItemOption] = field(default_factory=list)


@dataclass(frozen=True)
class OrderRecord:
    id: int
    order_uuid: UUID
    created_at: datetime
    total_price: Money
    items: list[OrderRecordItem]