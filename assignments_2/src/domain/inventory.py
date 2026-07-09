import copy
from dataclasses import dataclass, field

from src.domain.ingredient import Ingredient
from src.domain.inventory_item import InventoryItem
from src.domain.recipe import Recipe
from src.domain.exceptions import OutOfStockError
from src.domain.quantity import Quantity

@dataclass
class Inventory:
    items: list[InventoryItem] = field(default_factory=list)

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

    def _find_item(self, ingredient: Ingredient) -> InventoryItem:
        for item in self.items:
            if item.ingredient == ingredient:
                return item
            
        raise OutOfStockError()

    def consume(self, recipe: Recipe, menu_quantity: Quantity) -> None:
        for recipe_item in recipe.items:
            item = self._find_item(recipe_item.ingredient)

            item.decrease(recipe_item.quantity.multiply(menu_quantity))
    
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
            self.consume(recipe, menu_quantity)

    def can_consume_all(self, requirements: list[tuple[Recipe, Quantity]]) -> bool:
        # 깊은 복사로 원본과 독립적인 사본으로 검사
        simulation = copy.deepcopy(self)

        try:
            simulation.consume_all(requirements)
        except (OutOfStockError, ValueError):
            return False

        return True