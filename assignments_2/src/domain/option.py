from dataclasses import dataclass

from src.domain.money import Money

@dataclass
class Option:
    name: str
    additional_price: Money

    def __post_init__(self) -> None:
        if type(self.name) is not str:
            raise TypeError("Option name 은 문자열이여야 합니다.")
    
        self.name = self.name.strip()

        if not self.name:
            raise  ValueError("Option name 은 빈칸일 수 없습니다.")

        if type(self.additional_price) is not Money:
            raise TypeError("Option additional_price 은 Money 형 이여야 합니다.")
