from dataclasses import dataclass, field
from src.domain.money import Money
from src.domain.option_group import OptionGroup
from src.domain.option_item import OptionItem
from src.domain.recipe import Recipe
from src.domain.inventory import Inventory
from src.domain.quantity import Quantity
from src.domain.category import Category
from src.domain.menu_tag import MenuTag

@dataclass
class Menu:
    name: str
    price: Money
    recipe: Recipe
    category: Category = Category.COFFEE
    tags: list[MenuTag] = field(default_factory=list)
    option_groups: list[OptionGroup] = field(default_factory=list)
    is_sold_out: bool = False  # 관리자의 수동 품절 여부 (DB 저장 필드)

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

    def is_available(self, inventory: Inventory | None = None) -> bool:
        """
        주문 가능 여부 판정:
        1. 수동 품절(is_sold_out=True) 상태이면 False
        2. Inventory 객체가 제공되면 레시피 재고 충분 여부 검사 (기본 1개 기준)
        3. Inventory가 없으면 수동 품절 여부만 반영
        """
        if self.is_sold_out:
            return False
        if inventory is not None:
            return inventory.can_consume(self.recipe, Quantity(1))
        return True
    
    def set_available(self, value: bool) -> None:
        """관리자 수동 품절/판매재개 설정 (T/F)"""
        self.is_sold_out = not value

    def validate_orderable(self, inventory: Inventory | None = None) -> None:
        if not self.is_available(inventory):
            if self.is_sold_out:
                raise ValueError(f"'{self.name}' 메뉴는 관리자에 의해 판매 중지되었습니다.")
            raise ValueError(f"'{self.name}' 메뉴는 재고가 부족하여 품절입니다.")

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