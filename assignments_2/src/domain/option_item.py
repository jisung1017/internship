from dataclasses import dataclass, field

from src.domain.money import Money
from src.domain.recipe import Recipe


@dataclass
class OptionItem:
    name: str
    additional_price: Money
    recipe: Recipe = field(default_factory=lambda: Recipe(items=[]))

    def __post_init__(self) -> None:
        if not isinstance(self.name, str):
            raise TypeError("OptionItem name은 str 타입이어야 합니다.")
        self.name = self.name.strip()
        if not self.name:
            raise ValueError("OptionItem name은 비어있을 수 없습니다.")
        if not isinstance(self.additional_price, Money):
            raise TypeError("OptionItem additional_price는 Money 타입이어야 합니다.")
        if not isinstance(self.recipe, Recipe):
            raise TypeError("OptionItem recipe는 Recipe 타입이어야 합니다.")