from dataclasses import dataclass, field

from src.domain.money import Money
from src.domain.option_group import OptionGroup
from src.domain.recipe import Recipe

@dataclass
class Menu:
    name: str
    price: Money
    recipe: Recipe
    option_groups: list[OptionGroup] = field(default_factory=list)

    def __post_init__(self):
        if type(self.name) is not str:
            raise TypeError("Menu 이름은 문자열이여야 합니다.")
    
        self.name = self.name.strip()
        if not self.name:
            raise  ValueError("Menu 이름은 빈칸일 수 없습니다.")
        
        if type(self.price) is not Money:
            raise TypeError("Menu 가격은 Money 데이터형이어야 합니다.")
    
        if type(self.recipe) is not Recipe:
            raise TypeError("Recipe 는 Recipe 타입이여야 합니다.")
        
        if type(self.option_groups) is not list:
            raise TypeError("Menu OptionGroup 은 list 여야 합니다.")
            
        for option_group in self.option_groups:
            if type(option_group) is not OptionGroup:
                raise TypeError("OptionGroup 으로만 이루어져야 합니다.")
