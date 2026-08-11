from dataclasses import dataclass, field

from src.domain.money import Money
from src.domain.option import Option
from src.domain.option_group import OptionGroup
from src.domain.recipe import Recipe


@dataclass
class Menu:
    name: str
    price: Money
    recipe: Recipe
    option_groups: list[OptionGroup] = field(default_factory=list)

    def __post_init__(self):
        if not isinstance(self.name, str):
            raise TypeError("Menu 이름은 문자열이여야 합니다.")
    
        self.name = self.name.strip()
        if not self.name:
            raise  ValueError("Menu 이름은 빈칸일 수 없습니다.")
        
        if not isinstance(self.price, Money):
            raise TypeError("Menu 가격은 Money 데이터형이어야 합니다.")
    
        if not isinstance(self.recipe, Recipe):
            raise TypeError("Recipe 는 Recipe 타입이여야 합니다.")
        
        if not isinstance(self.option_groups, list):
            raise TypeError("Menu OptionGroup 은 list 여야 합니다.")
            
        for option_group in self.option_groups:
            if not isinstance(option_group, OptionGroup):
                raise TypeError("OptionGroup 으로만 이루어져야 합니다.")

    def contains_option(self, option: Option) -> bool:
        """이 메뉴에 속한 옵션 그룹 중 해당 옵션을 포함하는 그룹이 있는지 확인합니다."""
        return any(group.contains(option) for group in self.option_groups)

    def find_option_by_name(self, name: str) -> Option | None:
        """옵션 이름을 통해 메뉴 내의 해당 옵션 객체를 탐색합니다."""
        for group in self.option_groups:
            option = group.find_option_by_name(name)
            if option is not None:
                return option
        return None

    def validate_selected_options(self, selected_options: list[Option]) -> None:
        for option in selected_options:
            if not self.contains_option(option):
                raise ValueError(
                    f"{option.name} 옵션은 이 메뉴에서 선택할 수 없습니다."
                )

        for group in self.option_groups:
            group.validate(selected_options)