from dataclasses import dataclass, field

from src.domain.menu import Menu
from src.domain.option import Option
from src.domain.option_group import OptionGroup
from src.domain.quantity import Quantity

MIN_ORDER_QUANTITY = Quantity(1)
MAX_ORDER_QUANTITY = Quantity(10)


@dataclass
class PendingOrder:
    """지금 사용자가 조립 중인 주문 한 건 (메뉴 + 옵션 + 수량)."""

    menu: Menu
    selected_options: list[Option] = field(default_factory=list)
    quantity: Quantity | None = None
    group_index: int = 0

    def current_option_group(self) -> OptionGroup | None:
        groups = self.menu.option_groups

        if self.group_index >= len(groups):
            return None

        return groups[self.group_index]

    def is_option_selection_done(self) -> bool:
        return self.current_option_group() is None

    def select_current_option_group(self, selected: list[Option]) -> None:
        if self.is_option_selection_done():
            raise ValueError("선택할 옵션 그룹이 없습니다.")

        self.selected_options += selected
        self.group_index += 1

    def set_quantity(self, quantity: Quantity) -> None:
        if quantity.is_greater_than(MAX_ORDER_QUANTITY) or MIN_ORDER_QUANTITY.is_greater_than(quantity):
            raise ValueError(f"수량은 {MIN_ORDER_QUANTITY}~{MAX_ORDER_QUANTITY} 사이여야 합니다.")

        self.quantity = quantity

    def is_ready(self) -> bool:
        return self.is_option_selection_done() and self.quantity is not None