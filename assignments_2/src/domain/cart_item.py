from dataclasses import dataclass, field

from src.domain.menu import Menu
from src.domain.money import Money
from src.domain.option import Option
from src.domain.quantity import Quantity
from src.domain.recipe import Recipe


@dataclass
class CartItem:
    menu: Menu
    quantity: Quantity
    selected_options: list[Option] = field(default_factory=list)

    def __post_init__(self):
        if not isinstance(self.menu, Menu):
            raise TypeError("CartItem menu는 Menu 타입이어야 합니다.")

        if not isinstance(self.quantity, Quantity):
            raise TypeError("CartItem quantity는 Quantity 타입이어야 합니다.")

        if not isinstance(self.selected_options, list) :
            raise TypeError("CartItem selected_options는 list 타입이어야 합니다.")

        for option in self.selected_options:
            if not isinstance(option, Option):
                raise TypeError(
                    "CartItem selected_options는 Option 타입으로만 이루어져야 합니다."
                )

    def unit_price(self) -> Money:
        """메뉴 기본 가격과 선택된 옵션 추가금을 합산한 1잔당 단가를 계산합니다."""
        option_total = Money(0)
        for option in self.selected_options:
            option_total = option_total.add(option.additional_price)

        return self.menu.price.add(option_total)

    def total_price(self) -> Money:
        """단가(unit_price)에 수량을 곱해 해당 장바구니 항목의 총 가격을 계산합니다."""
        return self.unit_price().multiply(self.quantity)

    def get_recipe_requirements(self) -> list[tuple[Recipe, Quantity]]:
        """해당 주문 항목(메뉴 + 옵션)이 필요로 하는 레시피 요구량 목록을 반환합니다."""
        requirements: list[tuple[Recipe, Quantity]] = [(self.menu.recipe, self.quantity)]
        requirements.extend(
            (option.recipe, self.quantity) for option in self.selected_options
        )
        return requirements