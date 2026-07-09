from dataclasses import dataclass
from typing import Dict, List

from example_2.interfaces.domain.cart import Cart
from example_2.interfaces.domain.inventory import Inventory
from example_2.interfaces.domain.recipe import Recipe


@dataclass
class InventoryService:
    def check_available(
        self,
        cart: Cart,
        recipes: List[Recipe],
        inventories: List[Inventory],
    ):
        required_amounts = self._calculate_required_amounts(cart, recipes)
        inventory_by_ingredient_id = self._map_inventory_by_ingredient_id(inventories)

        for ingredient_id, required_amount in required_amounts.items():
            inventory = inventory_by_ingredient_id.get(ingredient_id)
            if inventory is None:
                raise ValueError("재고 정보를 찾을 수 없어요.")
            if inventory.check_inventory_amount() < required_amount:
                raise ValueError("재고가 부족해요.")

    def decrease_stock(
        self,
        cart: Cart,
        recipes: List[Recipe],
        inventories: List[Inventory],
    ):
        self.check_available(cart, recipes, inventories)

        required_amounts = self._calculate_required_amounts(cart, recipes)
        inventory_by_ingredient_id = self._map_inventory_by_ingredient_id(inventories)

        for ingredient_id, required_amount in required_amounts.items():
            inventory_by_ingredient_id[ingredient_id].outbound(required_amount)

    def _calculate_required_amounts(
        self,
        cart: Cart,
        recipes: List[Recipe],
    ):
        recipe_by_menu_id = {recipe.menu_id: recipe for recipe in recipes}
        required_amounts: Dict[int, int] = {}

        for item in cart.items:
            recipe = recipe_by_menu_id.get(item.menu.id)
            if recipe is None:
                raise ValueError("메뉴의 레시피를 찾을 수 없어요.")

            for recipe_ingredient in recipe.ingredients:
                ingredient_id = recipe_ingredient.ingredient.id
                required_amounts[ingredient_id] = (
                    required_amounts.get(ingredient_id, 0) + recipe_ingredient.amount
                )

        return required_amounts

    def _map_inventory_by_ingredient_id(self, inventories: List[Inventory]):
        return {inventory.ingredient_id: inventory for inventory in inventories}
