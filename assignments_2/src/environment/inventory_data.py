from src.domain.ingredient import Ingredient
from src.domain.inventory import Inventory
from src.domain.inventory_item import InventoryItem
from src.domain.quantity import Quantity

def create_inventory() -> Inventory:
    return Inventory(
        items=[
            InventoryItem(Ingredient("원두"), Quantity(1000)),
            InventoryItem(Ingredient("물"), Quantity(5000)),
            InventoryItem(Ingredient("우유"), Quantity(3000)),
            InventoryItem(Ingredient("컵"), Quantity(100)),
        ]
    )