from dataclasses import dataclass, field
from src.domain.money import Money
from src.domain.option_group import OptionGroup
from src.domain.option_item import OptionItem
from src.domain.recipe import Recipe


@dataclass
class Menu:
    name: str
    price: Money
    recipe: Recipe
    option_groups: list[OptionGroup] = field(default_factory=list)

    def __post_init__(self):
        if not isinstance(self.name, str):
            raise TypeError("Menu 이름은 str 타입이어야 합니다.")
        self.name = self.name.strip()
        if not self.name:
            raise ValueError("Menu 이름은 비어있을 수 없습니다.")
        if not isinstance(self.price, Money):
            raise TypeError("Menu 가격은 Money 타입이어야 합니다.")
        if not isinstance(self.recipe, Recipe):
            raise TypeError("Recipe는 Recipe 타입이어야 합니다.")
        if not isinstance(self.option_groups, list):
            raise TypeError("Menu OptionGroup은 list 타입이어야 합니다.")
        for option_group in self.option_groups:
            if not isinstance(option_group, OptionGroup):
                raise TypeError("OptionGroup 리스트에는 OptionGroup만 포함되어야 합니다.")

    def contains_option(self, option: OptionItem) -> bool:
        return any(group.contains(option) for group in self.option_groups)

    def find_option_by_name(self, name: str) -> OptionItem | None:
        for group in self.option_groups:
            option = group.find_option_by_name(name)
            if option is not None:
                return option
        return None

    def find_option_item_by_id(self, item_id: int) -> OptionItem | None:
        """옵션 아이템의 PK ID로 도메인 객체를 탐색합니다."""
        for group in self.option_groups:
            for item in group.options:
                if item.id == item_id:
                    return item
        return None

    def validate_selected_options(self, selected_options: list[OptionItem]) -> None:
        for option in selected_options:
            if not self.contains_option(option):
                raise ValueError(f"{option.name}은(는) 유효한 옵션이 아닙니다.")
        for group in self.option_groups:
            group.validate(selected_options)