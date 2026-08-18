import copy
from dataclasses import dataclass, field

from src.domain.ingredient import Ingredient
from src.domain.inventory_item import InventoryItem
from src.domain.inventory_history import InventoryHistory
from src.domain.recipe import Recipe
from src.domain.exceptions import OutOfStockError
from src.domain.quantity import Quantity

@dataclass
class Inventory:
    items: list[InventoryItem] = field(default_factory=list)
    history: list[InventoryHistory] = field(default_factory=list)

    def __post_init__(self):
        if not isinstance(self.items, list):
            raise TypeError("Inventory items 는 list 형 이여야 한다.")

        for item in self.items:
            if not isinstance(item, InventoryItem):
                raise TypeError("Inventory item 은 InventoryItem 형 이여야 한다.")

        ingredient_names = set()
        for item in self.items:
            if item.ingredient.name in ingredient_names:
                raise ValueError("Inventory 에는 동일한 재료가 중복될 수 없다.")

            ingredient_names.add(item.ingredient.name)

        if not isinstance(self.history, list):
            raise TypeError("Inventory history 는 list 형 이여야 한다.")

    def _find_item(self, ingredient: Ingredient) -> InventoryItem:
        for item in self.items:
            if item.ingredient == ingredient:
                return item

        raise OutOfStockError()

    def _record(self, ingredient: Ingredient, change: int, reason: str) -> None:
        self.history.append(InventoryHistory(ingredient=ingredient, change=change, reason=reason))

    def _consume(self, recipe: Recipe, menu_quantity: Quantity) -> None:
        for recipe_item in recipe.items:
            item = self._find_item(recipe_item.ingredient)
            required = recipe_item.quantity.multiply(menu_quantity)

            item.decrease(required)
            self._record(recipe_item.ingredient, -required.value, "CONSUME")

    def can_consume(self, recipe: Recipe, menu_quantity: Quantity) -> bool:
        try:
            for recipe_item in recipe.items:
                item = self._find_item(recipe_item.ingredient)
                required_quantity = recipe_item.quantity.multiply(menu_quantity)

                if required_quantity.is_greater_than(item.quantity):
                    return False

        except OutOfStockError:
            return False

        return True

    def consume_all(self, requirements: list[tuple[Recipe, Quantity]]) -> None:
        for recipe, menu_quantity in requirements:
            self._consume(recipe, menu_quantity)

    def can_consume_all(self, requirements: list[tuple[Recipe, Quantity]]) -> bool:
        # 깊은 복사로 원본과 독립적인 사본으로 검사
        simulation = copy.deepcopy(self)

        try:
            simulation.consume_all(requirements)
        except (OutOfStockError, ValueError):
            return False

        return True

    def restock(self, ingredient: Ingredient, quantity: Quantity, reason: str = "RESTOCK") -> None:
        if not isinstance(ingredient, Ingredient):
            raise TypeError("restock ingredient 는 Ingredient 타입이어야 합니다.")

        if not isinstance(quantity, Quantity):
            raise TypeError("restock quantity 는 Quantity 타입이어야 합니다.")

        if quantity.value == 0:
            raise ValueError("보충 수량은 0보다 커야 합니다.")
        
        # 기존 재고에 없는 원재료인 경우 ValueError 발생 (자동 추가 방지)
        try:
            item = self._find_item(ingredient)
        except OutOfStockError:
            raise ValueError(
                f"등록되지 않은 원재료('{ingredient.name}')는 재고를 보충할 수 없습니다."
            )

        item.increase(quantity)
        self._record(ingredient, quantity.value, reason)

    def get_quantity(self, ingredient: Ingredient) -> Quantity:
        try:
            return self._find_item(ingredient).quantity
        except OutOfStockError:
            return Quantity(0)