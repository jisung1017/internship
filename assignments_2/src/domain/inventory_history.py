from dataclasses import dataclass, field
from datetime import datetime

from src.domain.ingredient import Ingredient

REASONS = {"RESTOCK", "CONSUME", "CANCEL"}


@dataclass(frozen=True)
class InventoryHistory:
    ingredient: Ingredient
    change: int  # 양수=입고, 음수=소비
    reason: str
    timestamp: datetime = field(default_factory=datetime.now)
    id: int | None = None  

    def __post_init__(self) -> None:
        if not isinstance(self.ingredient, Ingredient):
            raise TypeError("InventoryHistory ingredient는 Ingredient 타입이어야 합니다.")

        if not isinstance(self.change, int) or isinstance(self.change, bool):
            raise TypeError("InventoryHistory change는 int 타입이어야 합니다.")

        if self.change == 0:
            raise ValueError("InventoryHistory change는 0이 될 수 없습니다.")

        if self.reason not in REASONS:
            raise ValueError(f"reason은 {REASONS} 중 하나여야 합니다.")