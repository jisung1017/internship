from dataclasses import dataclass, field
from src.domain.menu import Menu
from src.domain.money import Money
from src.domain.option_item import OptionItem
from src.domain.quantity import Quantity
from src.domain.recipe import Recipe

@dataclass
class CartItem:
    menu: Menu
    quantity: Quantity
    selected_options: list[OptionItem] = field(default_factory=list)

    def __post_init__(self):
        if not isinstance(self.menu, Menu):
            raise TypeError("CartItem menu는 Menu 타입이어야 합니다.")
        if not isinstance(self.quantity, Quantity):
            raise TypeError("CartItem quantity는 Quantity 타입이어야 합니다.")
        if not isinstance(self.selected_options, list):
            raise TypeError("CartItem selected_options는 list 타입이어야 합니다.")
        for option in self.selected_options:
            if not isinstance(option, OptionItem):
                raise TypeError("CartItem selected_options 요소는 OptionItem이어야 합니다.")

    def unit_price(self) -> Money:
        option_total = Money(0)
        for option in self.selected_options:
            option_total = option_total.add(option.additional_price)
        return self.menu.price.add(option_total)

    def total_price(self) -> Money:
        return self.unit_price().multiply(self.quantity)

    def get_recipe_requirements(self) -> list[tuple[Recipe, Quantity]]:
        requirements: list[tuple[Recipe, Quantity]] = [(self.menu.recipe, self.quantity)]
        requirements.extend(
            (option.recipe, self.quantity) for option in self.selected_options
        )
        return requirements