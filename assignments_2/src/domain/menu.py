from dataclasses import dataclass

from src.domain.money import Money

@dataclass
class Menu:
    name: str
    price: Money

    def __post_init__(self):
        if type(self.name) is not str:
            raise TypeError("Menu 이름은 문자열이여야 합니다.")
    
        self.name = self.name.strip()
        if not self.name:
            raise  ValueError("Menu 이름은 빈칸일 수 없습니다.")
        
        if type(self.price) is not Money:
            raise TypeError("Menu 가격은 Money 데이터형이어야 합니다.")
    