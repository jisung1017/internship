from dataclasses import dataclass
from datetime import datetime

from src.domain.money import Money


@dataclass(frozen=True)
class OrderRecordItem:
    menu_name: str
    quantity: int
    line_total: Money


@dataclass(frozen=True)
class OrderRecord:
    id: int
    created_at: datetime
    total_price: Money
    items: list[OrderRecordItem]