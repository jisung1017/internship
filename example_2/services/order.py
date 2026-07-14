from dataclasses import dataclass
from typing import List

from example_2.interfaces.domain.cart import Cart
from example_2.interfaces.domain.inventory import Inventory
from example_2.interfaces.domain.recipe import Recipe
from example_2.services.inventory import InventoryService
from example_2.services.payment import PaymentResult, PaymentService


@dataclass
class OrderService:
    inventory_service: InventoryService
    payment_service: PaymentService

    def checkout(
        self,
        cart: Cart,
        recipes: List[Recipe],
        inventories: List[Inventory],
    ) -> PaymentResult:
        self.inventory_service.check_available(cart, recipes, inventories)
        payment_result = self.payment_service.pay(cart)
        self.inventory_service.decrease_stock(cart, recipes, inventories)
        return payment_result
