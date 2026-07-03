from dataclasses import dataclass, field

from src.domain.ingredient import Ingredient
from src.domain.inventory_item import InventoryItem
from src.domain.recipe import Recipe

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
            
        raise ValueError(f"{ingredient.name}의 재고가 존재하지 않습니다.")

    def consume(self, recipe: Recipe) -> None:
        for recipe_item in recipe.items:
            item = self._find_item(recipe_item.ingredient)
            item.decrease(recipe_item.quantity)