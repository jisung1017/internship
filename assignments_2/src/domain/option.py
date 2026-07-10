from dataclasses import dataclass, field

from src.domain.money import Money
from src.domain.recipe import Recipe

@dataclass
class Option:
    name: str
    additional_price: Money
    recipe: Recipe = field(default_factory=lambda: Recipe(items=[]))

    def __post_init__(self) -> None:
        if not isinstance(self.name, str):
            raise TypeError("Option name 은 문자열이여야 합니다.")
    
        self.name = self.name.strip()

        if not self.name:
            raise  ValueError("Option name 은 빈칸일 수 없습니다.")

        if not isinstance(self.additional_price, Money):
            raise TypeError("Option additional_price 은 Money 형 이여야 합니다.")

        if not isinstance(self.recipe, Recipe):
            raise TypeError("Option recipe 는 Recipe 형 이여야 합니다.")