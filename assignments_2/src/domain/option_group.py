from dataclasses import dataclass, field

from src.domain.option import Option
from src.domain.quantity import Quantity

@dataclass
class OptionGroup:
    name: str
    min_quantity: Quantity
    max_quantity: Quantity
    options: list[Option] = field(default_factory=list)

    def __post_init__(self):
        if type(self.name) is not str:
            raise TypeError("OptionGroup 이름은 문자열이여야 합니다.")
    
        self.name = self.name.strip()
        if not self.name:
            raise  ValueError("OptionGroup 이름은 빈칸일 수 없습니다.")
        
        if type(self.options) is not list:
            raise TypeError("OptionGroup options 는 list 여야 합니다.")
        
        for option in self.options:
            if type(option) is not Option:
                raise TypeError("OptionGroup options 는 Option 타입으로만 이루어져야 합니다.")

        if not isinstance(self.min_quantity, Quantity):
            raise TypeError("OptionGroup min_quantity 는 Quantity 자료형 이여야 합니다.")
             
        if not isinstance(self.max_quantity, Quantity):
            raise TypeError("OptionGroup max_quantity 는 Quantity 자료형 이여야 합니다.")
        
        if self.min_quantity.is_greater_than(self.max_quantity):
            raise ValueError("최소 수량은 최대 수량보다 많을 수 없습니다.")