from dataclasses import dataclass, field
from src.domain.option_item import OptionItem
from src.domain.quantity import Quantity

SELECTION_MODES = {"choice", "count"}


@dataclass
class Option:
    """옵션 마스터 (대분류) - 기본 제약조건(default)을 보유"""
    name: str
    default_min: Quantity = field(default_factory=lambda: Quantity(0))
    default_max: Quantity = field(default_factory=lambda: Quantity(1))
    selection_mode: str = "choice"
    items: list[OptionItem] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not isinstance(self.name, str):
            raise TypeError("Option name은 str 타입이어야 합니다.")
        self.name = self.name.strip()
        if not self.name:
            raise ValueError("Option name은 비어있을 수 없습니다.")
        if not isinstance(self.default_min, Quantity):
            raise TypeError("Option default_min은 Quantity 타입이어야 합니다.")
        if not isinstance(self.default_max, Quantity):
            raise TypeError("Option default_max는 Quantity 타입이어야 합니다.")
        if self.default_min.is_greater_than(self.default_max):
            raise ValueError("기본 최소 선택 수량이 기본 최대 선택 수량보다 클 수 없습니다.")
        if self.selection_mode not in SELECTION_MODES:
            raise ValueError(f"selection_mode는 {SELECTION_MODES} 중 하나여야 합니다.")
        if not isinstance(self.items, list):
            raise TypeError("Option items는 list 타입이어야 합니다.")
        for item in self.items:
            if not isinstance(item, OptionItem):
                raise TypeError("Option items 요소는 OptionItem 타입이어야 합니다.")