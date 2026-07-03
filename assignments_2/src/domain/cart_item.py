from dataclasses import dataclass,field

from src.domain.menu import Menu
from src.domain.option import Option
from src.domain.quantity import Quantity

@dataclass
class CartItem:
    menu: Menu
    quantity: Quantity
    selected_options: list[Option] = field(default_factory=list)

    def __post_init__(self):
        if type(self.menu) is not Menu:
            raise TypeError("CartItem menu는 Menu 타입이어야 합니다.")

        if type(self.quantity) is not Quantity:
            raise TypeError("CartItem quantity는 Quantity 타입이어야 합니다.")

        if type(self.selected_options) is not list:
            raise TypeError("CartItem selected_options는 list 타입이어야 합니다.")

        for option in self.selected_options:
            if type(option) is not Option:
                raise TypeError(
                    "CartItem selected_options는 Option 타입으로만 이루어져야 합니다."
                )