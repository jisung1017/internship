from dataclasses import dataclass, field
from src.domain.option_item import OptionItem

@dataclass
class Option:
    """옵션 대분류 (예: 온도, 사이즈, 시럽 추가)"""
    name: str
    items: list[OptionItem] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not isinstance(self.name, str):
            raise TypeError("Option name은 str 타입이어야 합니다.")
        self.name = self.name.strip()
        if not self.name:
            raise ValueError("Option name은 비어있을 수 없습니다.")
        if not isinstance(self.items, list):
            raise TypeError("Option items는 list 타입이어야 합니다.")
        for item in self.items:
            if not isinstance(item, OptionItem):
                raise TypeError("Option items 요소는 OptionItem 타입이어야 합니다.")